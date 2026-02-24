"""Roller485Util メソッドのテスト — シリアル通信をモックして検証."""

from __future__ import annotations

import struct
from unittest.mock import patch

import pytest

from roller485.roller485_protocol import Roller485Protocol as Proto
from roller485.util import Roller485Util

from tests.conftest import build_readback_response, build_setting_response


# ---------------------------------------------------------------------------
# 内部 Enum の値テスト
# ---------------------------------------------------------------------------


class TestEnums:
    """内部 Enum の値が期待通りであることを確認."""

    def test_switch_enum(self) -> None:
        assert Roller485Util.Switch.Off == 0
        assert Roller485Util.Switch.On == 1

    def test_motor_mode_enum(self) -> None:
        assert Roller485Util.MotorMode.Speed == 1
        assert Roller485Util.MotorMode.Position == 2
        assert Roller485Util.MotorMode.Current == 3
        assert Roller485Util.MotorMode.Encoder == 4

    def test_button_mode_enum(self) -> None:
        assert Roller485Util.ButtonMode.Off == 0
        assert Roller485Util.ButtonMode.On == 1

    def test_rs485_baud_rate_enum(self) -> None:
        assert Roller485Util.RS485BaudRate.Baud115200 == 0
        assert Roller485Util.RS485BaudRate.Baud19200 == 1
        assert Roller485Util.RS485BaudRate.Baud9600 == 2


# ---------------------------------------------------------------------------
# _setting — 送信パケットの構築検証
# ---------------------------------------------------------------------------


class TestSettingPacketBuild:
    """_setting() が正しいバイナリパケットを write() に渡すことを検証."""

    def test_motor_switch_on_packet(self, mock_roller: Roller485Util) -> None:
        """motor_switch ON のパケット構造を検証."""
        mock_roller._setting(Proto.CommandCode.motor_switch, data1=1)

        mock_roller.write.assert_called_once()  # type: ignore[union-attr]
        written: bytes = mock_roller.write.call_args[0][0]  # type: ignore[union-attr]

        assert len(written) == 15
        # first_byte = motor_switch (0x00)
        assert written[0] == 0x00
        # device_id = 0
        assert written[1] == 0x00
        # data1 = 1 (s4le)
        assert struct.unpack_from("<i", written, 2)[0] == 1
        # CRC8 が正しい
        expected_crc = Roller485Util.calculate_crc8(written[:-1])
        assert written[-1] == expected_crc

    def test_speed_control_packet(self, mock_roller: Roller485Util) -> None:
        """speed_control のパケットで data1/data2 が正しくエンコードされる."""
        speed = 100 * 100  # 100 RPM → 10000
        max_current = 500 * 100  # 500 mA → 50000

        mock_roller._setting(
            Proto.CommandCode.speed_control, data1=speed, data2=max_current
        )

        written: bytes = mock_roller.write.call_args[0][0]  # type: ignore[union-attr]
        d1 = struct.unpack_from("<i", written, 2)[0]
        d2 = struct.unpack_from("<i", written, 6)[0]
        assert d1 == speed
        assert d2 == max_current


# ---------------------------------------------------------------------------
# _setting_resp — レスポンス検証
# ---------------------------------------------------------------------------


class TestSettingResp:
    """_setting_resp() のレスポンスパース・CRC 検証テスト."""

    def test_valid_response_returns_true(self, mock_roller: Roller485Util) -> None:
        """正しいレスポンスで True を返す."""
        resp = build_setting_response(Proto.CommandCode.motor_switch_resp, data1=1)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller._setting_resp(Proto.CommandCode.motor_switch_resp, data1=1)
        assert result is True

    def test_wrong_data_returns_false(self, mock_roller: Roller485Util) -> None:
        """期待と異なる data1 で False を返す."""
        resp = build_setting_response(Proto.CommandCode.motor_switch_resp, data1=0)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller._setting_resp(Proto.CommandCode.motor_switch_resp, data1=1)
        assert result is False

    def test_bad_crc_returns_false(self, mock_roller: Roller485Util) -> None:
        """CRC8 が不正なレスポンスで False を返す."""
        resp = bytearray(
            build_setting_response(Proto.CommandCode.motor_switch_resp, data1=1)
        )
        # CRC を壊す
        resp[-1] ^= 0xFF
        mock_roller.read.return_value = bytes(resp)  # type: ignore[union-attr]

        result = mock_roller._setting_resp(Proto.CommandCode.motor_switch_resp, data1=1)
        assert result is False


# ---------------------------------------------------------------------------
# 設定系メソッド (motor_switch, mode_setting 等)
# ---------------------------------------------------------------------------


class TestMotorSwitch:
    """motor_switch() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_motor_switch_on(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.motor_switch_resp, data1=1)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.motor_switch(Roller485Util.Switch.On)
        assert result is True
        mock_roller.write.assert_called_once()  # type: ignore[union-attr]

    @patch("roller485.util.time.sleep")
    def test_motor_switch_off(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.motor_switch_resp, data1=0)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.motor_switch(Roller485Util.Switch.Off)
        assert result is True


class TestModeSetting:
    """mode_setting() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_set_speed_mode(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.mode_setting_resp, data1=1)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.mode_setting(Roller485Util.MotorMode.Speed)
        assert result is True

    @patch("roller485.util.time.sleep")
    def test_set_position_mode(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.mode_setting_resp, data1=2)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.mode_setting(Roller485Util.MotorMode.Position)
        assert result is True


class TestSaveToFlash:
    """save_to_flash() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_save_success(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.save_to_flash_resp, data1=1)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.save_to_flash()
        assert result is True


# ---------------------------------------------------------------------------
# データ変換ロジック (speed clipping, PID scaling, RGB encoding)
# ---------------------------------------------------------------------------


class TestSpeedAndMaxCurrent:
    """set_speed_and_max_current() のデータ変換テスト."""

    @patch("roller485.util.time.sleep")
    def test_speed_scaling(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """speed は *100 でスケーリングされる."""
        speed = 100
        max_current = 500.0
        expected_speed = speed * 100
        expected_current = int(max_current) * 100

        resp = build_setting_response(
            Proto.CommandCode.speed_control_resp,
            data1=expected_speed,
            data2=expected_current,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_speed_and_max_current(speed, max_current)
        assert result is True

        # 送信パケットの data1 を検証
        written: bytes = mock_roller.write.call_args[0][0]  # type: ignore[union-attr]
        d1 = struct.unpack_from("<i", written, 2)[0]
        assert d1 == expected_speed

    @patch("roller485.util.time.sleep")
    def test_speed_clipping_upper(
        self, _mock_sleep, mock_roller: Roller485Util
    ) -> None:
        """speed は 21_000_000 にクリッピングされる."""
        speed = 99_999_999  # 上限超過
        expected_speed = 21_000_000 * 100

        resp = build_setting_response(
            Proto.CommandCode.speed_control_resp,
            data1=expected_speed,
            data2=0,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        mock_roller.set_speed_and_max_current(speed, 0)

        written: bytes = mock_roller.write.call_args[0][0]  # type: ignore[union-attr]
        d1 = struct.unpack_from("<i", written, 2)[0]
        assert d1 == expected_speed

    @patch("roller485.util.time.sleep")
    def test_speed_clipping_lower(
        self, _mock_sleep, mock_roller: Roller485Util
    ) -> None:
        """speed は -21_000_000 にクリッピングされる."""
        speed = -99_999_999  # 下限超過
        expected_speed = -21_000_000 * 100

        resp = build_setting_response(
            Proto.CommandCode.speed_control_resp,
            data1=expected_speed,
            data2=0,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        mock_roller.set_speed_and_max_current(speed, 0)

        written: bytes = mock_roller.write.call_args[0][0]  # type: ignore[union-attr]
        d1 = struct.unpack_from("<i", written, 2)[0]
        assert d1 == expected_speed


class TestSpeedPid:
    """set_speed_pid() / set_position_pid() のスケーリングテスト."""

    @patch("roller485.util.time.sleep")
    def test_pid_scaling(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """PID 値は *100_000 でスケーリングされる."""
        p, i, d = 1.5, 0.1, 0.05
        int_p = int(p * 100_000)
        int_i = int(i * 100_000)
        int_d = int(d * 100_000)

        resp = build_setting_response(
            Proto.CommandCode.speed_pid_config_resp,
            data1=int_p,
            data2=int_i,
            data3=int_d,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_speed_pid(p, i, d)
        assert result is True

        written: bytes = mock_roller.write.call_args[0][0]  # type: ignore[union-attr]
        d1 = struct.unpack_from("<i", written, 2)[0]
        d2 = struct.unpack_from("<i", written, 6)[0]
        d3 = struct.unpack_from("<i", written, 10)[0]
        assert d1 == int_p
        assert d2 == int_i
        assert d3 == int_d


class TestRgbLedControl:
    """rgb_led_control() のエンコードテスト."""

    @patch("roller485.util.time.sleep")
    def test_rgb_encoding(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """r, g, b, mode が data1 に正しくエンコードされる."""
        r, g, b, mode, brightness = 255, 128, 64, 1, 80
        expected_data1 = r + g * 256 + b * 256 * 256 + mode * 256 * 256 * 256
        expected_data2 = brightness

        resp = build_setting_response(
            Proto.CommandCode.rgb_led_control_resp,
            data1=expected_data1,
            data2=expected_data2,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.rgb_led_control(
            r=r, g=g, b=b, mode=mode, brightness=brightness
        )
        assert result is True

    @patch("roller485.util.time.sleep")
    def test_rgb_clipping(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """RGB 値は 0-255、brightness は 0-100 にクリッピングされる."""
        # 上限超過
        r, g, b = 300, 300, 300
        brightness = 200
        clipped_r = 255
        clipped_g = 255
        clipped_b = 255
        clipped_brightness = 100

        expected_data1 = (
            clipped_r + clipped_g * 256 + clipped_b * 256 * 256 + 0 * 256 * 256 * 256
        )

        resp = build_setting_response(
            Proto.CommandCode.rgb_led_control_resp,
            data1=expected_data1,
            data2=clipped_brightness,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.rgb_led_control(
            r=r, g=g, b=b, mode=0, brightness=brightness
        )
        assert result is True


class TestSetCurrent:
    """set_current() のスケーリングテスト."""

    @patch("roller485.util.time.sleep")
    def test_current_scaling(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """current は *100 でスケーリングされる."""
        current = 500.5
        expected = int(min(1200, max(-1200, current)) * 100)

        resp = build_setting_response(
            Proto.CommandCode.current_control_resp, data1=expected
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_current(current)
        assert result is True

    @patch("roller485.util.time.sleep")
    def test_current_clipping(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """current は -1200〜1200 にクリッピングされる."""
        current = 9999.0
        expected = int(1200 * 100)

        resp = build_setting_response(
            Proto.CommandCode.current_control_resp, data1=expected
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_current(current)
        assert result is True


# ---------------------------------------------------------------------------
# 読取系メソッド (get_motor_status, get_other_status 等)
# ---------------------------------------------------------------------------


class TestGetMotorStatus:
    """get_motor_status() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_successful_read(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        """正常なレスポンスから dict を返す."""
        speed = 10000  # 100.00 RPM
        position = -50000  # -500.00 counts
        current = 25000  # 250.00 mA
        mode = 1
        status = 0
        error = 0

        payload = struct.pack("<iiiBBB", speed, position, current, mode, status, error)
        resp = build_readback_response(
            Proto.CommandCode.motor_status_readback_resp,
            payload_bytes=payload,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.get_motor_status()
        assert result["speed"] == pytest.approx(100.0)
        assert result["position"] == pytest.approx(-500.0)
        assert result["current"] == pytest.approx(250.0)
        assert result["mode"] == 1
        assert result["status"] == 0
        assert result["error"] == 0

    @patch("roller485.util.time.sleep")
    def test_bad_crc_returns_empty(
        self, _mock_sleep, mock_roller: Roller485Util
    ) -> None:
        """CRC8 不正時は空 dict を返す."""
        payload = struct.pack("<iiiBBB", 0, 0, 0, 0, 0, 0)
        resp = bytearray(
            build_readback_response(
                Proto.CommandCode.motor_status_readback_resp,
                payload_bytes=payload,
            )
        )
        resp[-1] ^= 0xFF  # CRC を壊す
        mock_roller.read.return_value = bytes(resp)  # type: ignore[union-attr]

        result = mock_roller.get_motor_status()
        assert result == {}


class TestGetOtherStatus:
    """get_other_status() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_successful_read(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        vin_x100 = 1200  # 12.00 V
        temp = 35
        encoder_counter = 500
        rgb_mode = 1
        rgb_brightness = 80
        reserve = 0

        payload = struct.pack(
            "<IiiBBB",
            vin_x100,
            temp,
            encoder_counter,
            rgb_mode,
            rgb_brightness,
            reserve,
        )
        resp = build_readback_response(
            Proto.CommandCode.other_status_readback_resp,
            payload_bytes=payload,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.get_other_status()
        assert result["vin"] == pytest.approx(12.0)
        assert result["temp"] == 35
        assert result["encoder_counter"] == 500
        assert result["rgb_mode"] == 1
        assert result["rgb_brightness"] == 80


class TestGetSpeedPidAndRgb:
    """get_speed_pid_and_rgb() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_successful_read(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        speed_p = 150_000  # 1.50000
        speed_i = 10_000  # 0.10000
        speed_d = 0
        rgb_b = 0
        rgb_g = 255
        rgb_r = 128

        payload = struct.pack("<IIIBBB", speed_p, speed_i, speed_d, rgb_b, rgb_g, rgb_r)
        resp = build_readback_response(
            Proto.CommandCode.readback_2_resp,
            payload_bytes=payload,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.get_speed_pid_and_rgb()
        assert result["speed_p"] == pytest.approx(1.5)
        assert result["speed_i"] == pytest.approx(0.1)
        assert result["speed_d"] == pytest.approx(0.0)
        assert result["rgb_r"] == 128
        assert result["rgb_g"] == 255
        assert result["rgb_b"] == 0


class TestGetPositionPidAndOther:
    """get_position_pid_and_other() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_successful_read(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        position_p = 200_000
        position_i = 5_000
        position_d = 1_000
        rs485_id = 3
        rs485_bps = 0
        button_switch_mode = 1

        payload = struct.pack(
            "<IIIBBB",
            position_p,
            position_i,
            position_d,
            rs485_id,
            rs485_bps,
            button_switch_mode,
        )
        resp = build_readback_response(
            Proto.CommandCode.readback_3_resp,
            payload_bytes=payload,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.get_position_pid_and_other()
        assert result["position_p"] == pytest.approx(2.0)
        assert result["position_i"] == pytest.approx(0.05)
        assert result["position_d"] == pytest.approx(0.01)
        assert result["rs485_id"] == 3
        assert result["rs485_bps"] == 0
        assert result["button_switch_mode"] == 1


# ---------------------------------------------------------------------------
# その他の設定コマンド
# ---------------------------------------------------------------------------


class TestRemoveProtection:
    """remove_protection() のテスト.

    NOTE: remove_protection() は _setting() を data2= で呼び出すが、
    data1 は必須の位置引数のため TypeError が発生する。
    これはソースコードのバグである。
    """

    @patch("roller485.util.time.sleep")
    def test_remove_protection_raises_type_error(
        self, _mock_sleep, mock_roller: Roller485Util
    ) -> None:
        with pytest.raises(TypeError):
            mock_roller.remove_protection(100)


class TestSetEncoder:
    """set_encoder() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_set_encoder(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.encoder_resp, data1=12345)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_encoder(12345)
        assert result is True


class TestButtonSwitchingMode:
    """button_switching_mode() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_button_mode_on(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(
            Proto.CommandCode.button_switch_mode_resp, data1=1
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.button_switching_mode(Roller485Util.ButtonMode.On)
        assert result is True


class TestSetDeviceId:
    """set_device_id() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_set_device_id(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.device_id_resp, data1=5)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_device_id(5)
        assert result is True

    @patch("roller485.util.time.sleep")
    def test_device_id_clipping(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.device_id_resp, data1=255)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_device_id(999)
        assert result is True


class TestMotorJamProtection:
    """set_motor_jam_protection() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_enable(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(
            Proto.CommandCode.motor_jam_protection_resp, data1=1
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_motor_jam_protection(True)
        assert result is True

    @patch("roller485.util.time.sleep")
    def test_disable(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(
            Proto.CommandCode.motor_jam_protection_resp, data1=0
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_motor_jam_protection(False)
        assert result is True


class TestPositionOverRangeProtection:
    """set_motor_position_over_range_protection() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_enable(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(
            Proto.CommandCode.motor_position_over_range_protection_resp,
            data1=1,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_motor_position_over_range_protection(True)
        assert result is True


class TestSetRs485BaudRate:
    """set_rs485_baud_rate() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_set_baud_115200(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        resp = build_setting_response(Proto.CommandCode.rs485_baud_rate_resp, data1=0)
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_rs485_baud_rate(Roller485Util.RS485BaudRate.Baud115200)
        assert result is True


class TestSetPositionAndMaxCurrent:
    """set_position_and_max_current() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_position_scaling(self, _mock_sleep, mock_roller: Roller485Util) -> None:
        position = 500
        max_current = 300.0
        expected_pos = position * 100
        expected_cur = int(max_current) * 100

        resp = build_setting_response(
            Proto.CommandCode.position_control_resp,
            data1=expected_pos,
            data2=expected_cur,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_position_and_max_current(position, max_current)
        assert result is True


class TestSetPositionPid:
    """set_position_pid() のテスト."""

    @patch("roller485.util.time.sleep")
    def test_position_pid_scaling(
        self, _mock_sleep, mock_roller: Roller485Util
    ) -> None:
        p, i, d = 2.0, 0.05, 0.01
        int_p = int(p * 100_000)
        int_i = int(i * 100_000)
        int_d = int(d * 100_000)

        resp = build_setting_response(
            Proto.CommandCode.position_pid_config_resp,
            data1=int_p,
            data2=int_i,
            data3=int_d,
        )
        mock_roller.read.return_value = resp  # type: ignore[union-attr]

        result = mock_roller.set_position_pid(p, i, d)
        assert result is True
