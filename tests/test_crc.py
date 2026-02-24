"""CRC8 計算・パケット長・replace_crc8 のテスト."""

from __future__ import annotations

import io
import struct

import pytest
from kaitaistruct import KaitaiStream

from roller485.roller485_protocol import Roller485Protocol as Proto
from roller485.util import Roller485Util


# ---------------------------------------------------------------------------
# calculate_crc8
# ---------------------------------------------------------------------------


class TestCalculateCrc8:
    """CRC8 チェックサムの計算テスト."""

    def test_empty_bytes(self) -> None:
        """空バイト列の CRC8 は 0."""
        assert Roller485Util.calculate_crc8(b"") == 0

    def test_single_byte_zero(self) -> None:
        assert Roller485Util.calculate_crc8(b"\x00") == 0

    def test_single_byte_nonzero(self) -> None:
        result = Roller485Util.calculate_crc8(b"\x01")
        assert 0 <= result <= 255
        # CRC8 (poly 0x8C) for 0x01
        assert result == 0x5E

    def test_all_0xff(self) -> None:
        data = b"\xff" * 4
        result = Roller485Util.calculate_crc8(data)
        assert 0 <= result <= 255

    def test_known_request_packet(self) -> None:
        """実際のリクエストパケット構造からの CRC8 計算.

        motor_switch ON (command=0x00, device_id=0x00, data1=1, data2=0, data3=0):
        バイト列: 00 00 01000000 00000000 00000000
        """
        # command(1) + device_id(1) + data1(4) + data2(4) + data3(4) = 14 bytes
        payload = struct.pack("<bb iii", 0x00, 0x00, 1, 0, 0)
        crc = Roller485Util.calculate_crc8(payload)
        assert 0 <= crc <= 255
        # CRC は決定論的なので、同じ入力で同じ出力
        assert Roller485Util.calculate_crc8(payload) == crc

    def test_deterministic(self) -> None:
        """同じ入力に対して常に同じ結果を返す."""
        data = b"\x12\x34\x56\x78"
        result1 = Roller485Util.calculate_crc8(data)
        result2 = Roller485Util.calculate_crc8(data)
        assert result1 == result2

    def test_different_inputs_different_results(self) -> None:
        """異なる入力は (通常) 異なる CRC を返す."""
        a = Roller485Util.calculate_crc8(b"\x01\x02")
        b = Roller485Util.calculate_crc8(b"\x03\x04")
        # 衝突の可能性はあるが、このテストデータでは異なるはず
        assert a != b

    def test_incrementing_bytes(self) -> None:
        data = bytes(range(256))
        result = Roller485Util.calculate_crc8(data)
        assert isinstance(result, int)
        assert 0 <= result <= 255


# ---------------------------------------------------------------------------
# get_packet_length
# ---------------------------------------------------------------------------


class TestGetPacketLength:
    """コマンドコードからパケット長を取得するテスト."""

    # --- リクエストコマンド (15 バイト固定) ---
    @pytest.mark.parametrize(
        "cmd",
        [
            Proto.CommandCode.motor_switch,  # 0x00
            Proto.CommandCode.mode_setting,  # 0x01
            Proto.CommandCode.remove_protection,  # 0x06
            Proto.CommandCode.save_to_flash,  # 0x07
            Proto.CommandCode.encoder,  # 0x08
            Proto.CommandCode.button_switch_mode,  # 0x09
            Proto.CommandCode.rgb_led_control,  # 0x0A
            Proto.CommandCode.rs485_baud_rate,  # 0x0B
            Proto.CommandCode.device_id,  # 0x0C
            Proto.CommandCode.motor_jam_protection,  # 0x0D
            Proto.CommandCode.motor_position_over_range_protection,  # 0x0E
        ],
    )
    def test_standard_request_15bytes(self, cmd: Proto.CommandCode) -> None:
        assert Roller485Util.get_packet_length(cmd.value) == 15

    # --- レスポンスコマンド (17 バイト = 15 + magic2) ---
    @pytest.mark.parametrize(
        "cmd",
        [
            Proto.CommandCode.motor_switch_resp,  # 0x10
            Proto.CommandCode.mode_setting_resp,  # 0x11
            Proto.CommandCode.remove_protection_resp,  # 0x16
            Proto.CommandCode.save_to_flash_resp,  # 0x17
            Proto.CommandCode.encoder_resp,  # 0x18
            Proto.CommandCode.button_switch_mode_resp,  # 0x19
            Proto.CommandCode.rgb_led_control_resp,  # 0x1A
            Proto.CommandCode.rs485_baud_rate_resp,  # 0x1B
            Proto.CommandCode.device_id_resp,  # 0x1C
            Proto.CommandCode.motor_jam_protection_resp,  # 0x1D
            Proto.CommandCode.motor_position_over_range_protection_resp,  # 0x1E
        ],
    )
    def test_standard_response_17bytes(self, cmd: Proto.CommandCode) -> None:
        assert Roller485Util.get_packet_length(cmd.value) == 17

    # --- ループ制御リクエスト (15 バイト) ---
    @pytest.mark.parametrize(
        "cmd",
        [
            Proto.CommandCode.speed_control,  # 0x20
            Proto.CommandCode.speed_pid_config,  # 0x21
            Proto.CommandCode.position_control,  # 0x22
            Proto.CommandCode.position_pid_config,  # 0x23
            Proto.CommandCode.current_control,  # 0x24
        ],
    )
    def test_loop_control_request_15bytes(self, cmd: Proto.CommandCode) -> None:
        assert Roller485Util.get_packet_length(cmd.value) == 15

    # --- ループ制御レスポンス (17 バイト) ---
    @pytest.mark.parametrize(
        "cmd",
        [
            Proto.CommandCode.speed_control_resp,  # 0x30
            Proto.CommandCode.speed_pid_config_resp,  # 0x31
            Proto.CommandCode.position_control_resp,  # 0x32
            Proto.CommandCode.position_pid_config_resp,  # 0x33
            Proto.CommandCode.current_control_resp,  # 0x34
        ],
    )
    def test_loop_control_response_17bytes(self, cmd: Proto.CommandCode) -> None:
        assert Roller485Util.get_packet_length(cmd.value) == 17

    # --- ステータスリードバック (リクエスト 4 バイト) ---
    @pytest.mark.parametrize(
        "cmd",
        [
            Proto.CommandCode.motor_status_readback,  # 0x40
            Proto.CommandCode.other_status_readback,  # 0x41
            Proto.CommandCode.readback_2,  # 0x42
            Proto.CommandCode.readback_3,  # 0x43
        ],
    )
    def test_readback_request_4bytes(self, cmd: Proto.CommandCode) -> None:
        assert Roller485Util.get_packet_length(cmd.value) == 4

    # --- ステータスリードバック (レスポンス 20 バイト) ---
    @pytest.mark.parametrize(
        "cmd",
        [
            Proto.CommandCode.motor_status_readback_resp,  # 0x50
            Proto.CommandCode.other_status_readback_resp,  # 0x51
            Proto.CommandCode.readback_2_resp,  # 0x52
            Proto.CommandCode.readback_3_resp,  # 0x53
        ],
    )
    def test_readback_response_20bytes(self, cmd: Proto.CommandCode) -> None:
        assert Roller485Util.get_packet_length(cmd.value) == 20

    # --- I2C コマンド ---
    def test_i2c_read_reg_req(self) -> None:
        assert Roller485Util.get_packet_length(0x60) == 8

    def test_i2c_write_reg_req(self) -> None:
        assert Roller485Util.get_packet_length(0x61) == 25

    def test_i2c_read_raw_req(self) -> None:
        assert Roller485Util.get_packet_length(0x62) == 5

    def test_i2c_write_raw_req(self) -> None:
        assert Roller485Util.get_packet_length(0x63) == 25

    def test_i2c_read_reg_resp(self) -> None:
        assert Roller485Util.get_packet_length(0x70) == 27

    def test_i2c_write_reg_resp(self) -> None:
        assert Roller485Util.get_packet_length(0x71) == 6

    def test_i2c_read_raw_resp(self) -> None:
        assert Roller485Util.get_packet_length(0x72) == 27

    def test_i2c_write_raw_resp(self) -> None:
        assert Roller485Util.get_packet_length(0x73) == 6


# ---------------------------------------------------------------------------
# replace_crc8
# ---------------------------------------------------------------------------


class TestReplaceCrc8:
    """replace_crc8 が CRC8 を正しく計算してパケット末尾に書き込むことを検証."""

    def test_request_packet_crc8_is_correct(self) -> None:
        """リクエストパケットの CRC8 が正しく計算される."""
        length = Roller485Util.get_packet_length(Proto.CommandCode.motor_switch.value)
        _io = KaitaiStream(io.BytesIO(bytes(length)))

        prot = Proto(_io)
        prot.first_byte = Proto.CommandCode.motor_switch
        prot.device_id = 0
        prot.crc8 = 0

        payload = Proto.ConfigPayload(None, prot, prot._root)
        payload.data1 = 1
        payload.data2 = 0
        payload.data3 = 0
        payload._check()

        prot.payload = payload
        prot._check()
        prot._write()

        Roller485Util.replace_crc8(prot)

        output = _io.to_byte_array()
        # CRC8 はパケット末尾の 1 バイト
        expected_crc = Roller485Util.calculate_crc8(bytes(output[:-1]))
        assert output[-1] == expected_crc

    def test_crc8_changes_with_different_data(self) -> None:
        """data1 を変えると CRC8 も変わる."""

        def build(data1: int) -> int:
            length = Roller485Util.get_packet_length(
                Proto.CommandCode.motor_switch.value
            )
            _io = KaitaiStream(io.BytesIO(bytes(length)))
            prot = Proto(_io)
            prot.first_byte = Proto.CommandCode.motor_switch
            prot.device_id = 0
            prot.crc8 = 0

            payload = Proto.ConfigPayload(None, prot, prot._root)
            payload.data1 = data1
            payload.data2 = 0
            payload.data3 = 0
            payload._check()

            prot.payload = payload
            prot._check()
            prot._write()
            Roller485Util.replace_crc8(prot)
            return int(_io.to_byte_array()[-1])

        crc_on = build(1)
        crc_off = build(0)
        assert crc_on != crc_off
