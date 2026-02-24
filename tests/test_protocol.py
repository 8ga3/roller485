"""Roller485Protocol のパース / シリアライズテスト."""

from __future__ import annotations

import io
import struct

from kaitaistruct import KaitaiStream

from roller485.roller485_protocol import Roller485Protocol as Proto
from roller485.util import Roller485Util


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _build_request_bytes(
    command: int,
    device_id: int,
    data1: int = 0,
    data2: int = 0,
    data3: int = 0,
) -> bytes:
    """リクエストパケットのバイト列を手動で構築する (15 バイト).

    構造: <command:u1> <device_id:u1> <data1:s4le> <data2:s4le> <data3:s4le> <crc8:u1>
    """
    body = struct.pack("<bb iii", command, device_id, data1, data2, data3)
    crc = Roller485Util.calculate_crc8(body)
    return body + bytes([crc])


def _build_response_bytes(
    command: int,
    device_id: int,
    data1: int = 0,
    data2: int = 0,
    data3: int = 0,
) -> bytes:
    """レスポンスパケットのバイト列を手動で構築する (17 バイト).

    構造: 0xAA 0x55 <command:u1> <device_id:u1>
           <data1:s4le> <data2:s4le> <data3:s4le> <crc8:u1>
    """
    payload = struct.pack("<bb iii", command, device_id, data1, data2, data3)
    crc = Roller485Util.calculate_crc8(payload)
    return b"\xaa\x55" + payload + bytes([crc])


# ---------------------------------------------------------------------------
# CommandCode Enum
# ---------------------------------------------------------------------------


class TestCommandCode:
    """CommandCode 列挙値の正確性."""

    def test_motor_switch(self) -> None:
        assert Proto.CommandCode.motor_switch == 0x00

    def test_motor_switch_resp(self) -> None:
        assert Proto.CommandCode.motor_switch_resp == 0x10

    def test_speed_control(self) -> None:
        assert Proto.CommandCode.speed_control == 0x20

    def test_speed_control_resp(self) -> None:
        assert Proto.CommandCode.speed_control_resp == 0x30

    def test_motor_status_readback(self) -> None:
        assert Proto.CommandCode.motor_status_readback == 0x40

    def test_motor_status_readback_resp(self) -> None:
        assert Proto.CommandCode.motor_status_readback_resp == 0x50

    def test_i2c_read_register(self) -> None:
        assert Proto.CommandCode.i2c_read_register == 0x60

    def test_i2c_read_register_resp(self) -> None:
        assert Proto.CommandCode.i2c_read_register_resp == 0x70


# ---------------------------------------------------------------------------
# is_response / command_val プロパティ
# ---------------------------------------------------------------------------


class TestIsResponse:
    """is_response プロパティのテスト."""

    def test_request_is_not_response(self) -> None:
        """first_byte != 0xAA → リクエスト."""
        data = _build_request_bytes(
            Proto.CommandCode.motor_switch.value,
            device_id=0,
            data1=1,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.is_response is False

    def test_response_is_response(self) -> None:
        """first_byte == 0xAA → レスポンス."""
        data = _build_response_bytes(
            Proto.CommandCode.motor_switch_resp.value,
            device_id=0,
            data1=1,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.is_response is True


class TestCommandVal:
    """command_val プロパティのテスト."""

    def test_request_command_val(self) -> None:
        """リクエストでは first_byte がコマンドコードになる."""
        data = _build_request_bytes(
            Proto.CommandCode.mode_setting.value,
            device_id=0,
            data1=1,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.command_val == Proto.CommandCode.mode_setting

    def test_response_command_val(self) -> None:
        """レスポンスでは actual_command がコマンドコードになる."""
        data = _build_response_bytes(
            Proto.CommandCode.mode_setting_resp.value,
            device_id=0,
            data1=1,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.command_val == Proto.CommandCode.mode_setting_resp


# ---------------------------------------------------------------------------
# ConfigPayload パース
# ---------------------------------------------------------------------------


class TestConfigPayloadParse:
    """ConfigPayload のパースとフィールド検証."""

    def test_request_payload_fields(self) -> None:
        data = _build_request_bytes(
            Proto.CommandCode.motor_switch.value,
            device_id=5,
            data1=1,
            data2=200,
            data3=-300,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.device_id == 5
        assert prot.payload.data1 == 1
        assert prot.payload.data2 == 200
        assert prot.payload.data3 == -300

    def test_response_payload_fields(self) -> None:
        data = _build_response_bytes(
            Proto.CommandCode.motor_switch_resp.value,
            device_id=0,
            data1=1,
            data2=0,
            data3=0,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.payload.data1 == 1
        assert prot.payload.data2 == 0
        assert prot.payload.data3 == 0

    def test_negative_values(self) -> None:
        """負の値が signed int32 として正しくパースされる."""
        data = _build_request_bytes(
            Proto.CommandCode.speed_control.value,
            device_id=0,
            data1=-100_000,
            data2=-50_000,
        )
        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.payload.data1 == -100_000
        assert prot.payload.data2 == -50_000


# ---------------------------------------------------------------------------
# ReadbackReq パース (4 バイト)
# ---------------------------------------------------------------------------


class TestReadbackReqParse:
    """ReadbackReq (ステータス読み出しリクエスト) のパーステスト."""

    def test_readback_request_parse(self) -> None:
        """motor_status_readback リクエスト (4 バイト):
        <cmd:u1> <dev_id:u1> <read_flag:u1> <crc8:u1>
        """
        cmd = Proto.CommandCode.motor_status_readback.value
        dev_id = 0
        read_flag = 0
        body = struct.pack("<bbb", cmd, dev_id, read_flag)
        crc = Roller485Util.calculate_crc8(body)
        data = body + bytes([crc])

        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()
        assert prot.command_val == Proto.CommandCode.motor_status_readback
        assert prot.payload.read_flag == 0


# ---------------------------------------------------------------------------
# MotorStatusResp パース (20 バイト)
# ---------------------------------------------------------------------------


class TestMotorStatusRespParse:
    """MotorStatusResp のパーステスト."""

    def test_motor_status_response_parse(self) -> None:
        """motor_status_readback_resp を手動構築してパース."""
        cmd = Proto.CommandCode.motor_status_readback_resp.value
        dev_id = 0

        # ペイロード: speed(s4le), position(s4le), current(s4le),
        #             mode(u1), status(u1), error(u1)
        speed = 10000  # 100.00 RPM
        position = -50000  # -500.00 counts
        current = 25000  # 250.00 mA
        mode = 1
        status = 0
        error = 0

        payload = struct.pack("<iiiBBB", speed, position, current, mode, status, error)
        # レスポンスフレーム: AA 55 <cmd> <dev_id> <payload> <crc8>
        body = struct.pack("<bb", cmd, dev_id) + payload
        crc = Roller485Util.calculate_crc8(body)
        data = b"\xaa\x55" + body + bytes([crc])

        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()

        assert prot.is_response is True
        assert prot.command_val == Proto.CommandCode.motor_status_readback_resp
        assert prot.payload.speed == speed
        assert prot.payload.position == position
        assert prot.payload.current == current
        assert prot.payload.mode == mode
        assert prot.payload.status == status
        assert prot.payload.error == error


# ---------------------------------------------------------------------------
# OtherStatusResp パース
# ---------------------------------------------------------------------------


class TestOtherStatusRespParse:
    """OtherStatusResp のパーステスト."""

    def test_other_status_response_parse(self) -> None:
        cmd = Proto.CommandCode.other_status_readback_resp.value
        dev_id = 0

        # ペイロード: vin_x100(u4le), temp(s4le), encoder_counter(s4le),
        #             rgb_mode(u1), rgb_brightness(u1), reserve(u1)
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
        body = struct.pack("<bb", cmd, dev_id) + payload
        crc = Roller485Util.calculate_crc8(body)
        data = b"\xaa\x55" + body + bytes([crc])

        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()

        assert prot.payload.vin_x100 == vin_x100
        assert prot.payload.temp == temp
        assert prot.payload.encoder_counter == encoder_counter
        assert prot.payload.rgb_mode == rgb_mode
        assert prot.payload.rgb_brightness == rgb_brightness


# ---------------------------------------------------------------------------
# Readback2Resp / Readback3Resp パース
# ---------------------------------------------------------------------------


class TestReadback2RespParse:
    """Readback2Resp のパーステスト."""

    def test_readback2_parse(self) -> None:
        cmd = Proto.CommandCode.readback_2_resp.value
        dev_id = 0

        # ペイロード: speed_p(u4le), speed_i(u4le), speed_d(u4le),
        #             rgb_b(u1), rgb_g(u1), rgb_r(u1)
        speed_p = 150_000  # 1.50000
        speed_i = 10_000  # 0.10000
        speed_d = 0
        rgb_b = 0
        rgb_g = 255
        rgb_r = 128

        payload = struct.pack("<IIIBBB", speed_p, speed_i, speed_d, rgb_b, rgb_g, rgb_r)
        body = struct.pack("<bb", cmd, dev_id) + payload
        crc = Roller485Util.calculate_crc8(body)
        data = b"\xaa\x55" + body + bytes([crc])

        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()

        assert prot.payload.speed_p == speed_p
        assert prot.payload.speed_i == speed_i
        assert prot.payload.speed_d == speed_d
        assert prot.payload.rgb_r == rgb_r
        assert prot.payload.rgb_g == rgb_g
        assert prot.payload.rgb_b == rgb_b


class TestReadback3RespParse:
    """Readback3Resp のパーステスト."""

    def test_readback3_parse(self) -> None:
        cmd = Proto.CommandCode.readback_3_resp.value
        dev_id = 0

        # ペイロード: position_p(u4le), position_i(u4le), position_d(u4le),
        #             rs485_id(u1), rs485_bps(u1), button_switch_mode(u1)
        position_p = 200_000
        position_i = 5_000
        position_d = 1_000
        rs485_id = 3
        rs485_bps = 0  # 115200
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
        body = struct.pack("<bb", cmd, dev_id) + payload
        crc = Roller485Util.calculate_crc8(body)
        data = b"\xaa\x55" + body + bytes([crc])

        prot = Proto(KaitaiStream(io.BytesIO(data)))
        prot._read()

        assert prot.payload.position_p == position_p
        assert prot.payload.position_i == position_i
        assert prot.payload.position_d == position_d
        assert prot.payload.rs485_id == rs485_id
        assert prot.payload.rs485_bps == rs485_bps
        assert prot.payload.button_switch_mode == button_switch_mode


# ---------------------------------------------------------------------------
# ラウンドトリップテスト
# ---------------------------------------------------------------------------


class TestRoundTrip:
    """バイト列 → _read() → _write() → バイト列 が一致するラウンドトリップテスト."""

    def test_request_round_trip(self) -> None:
        """リクエストパケットのラウンドトリップ."""
        original = _build_request_bytes(
            Proto.CommandCode.speed_control.value,
            device_id=0,
            data1=100_000,
            data2=50_000,
        )
        # 読み込み
        prot = Proto(KaitaiStream(io.BytesIO(original)))
        prot._read()

        # 書き出し — _write() はストリーム全体を書き直す
        out_io = KaitaiStream(io.BytesIO(bytes(len(original))))
        prot._io = out_io
        prot._write()
        result = bytes(out_io.to_byte_array())

        # CRC8 以外のフィールドが一致
        assert result[:-1] == original[:-1]
        # CRC8 も一致 (replace_crc8 は _write 内で呼ばれないが、
        # 値は読み込み時に保存されているのでそのまま書かれる)
        assert result[-1] == original[-1]

    def test_response_round_trip(self) -> None:
        """レスポンスパケットのラウンドトリップ."""
        original = _build_response_bytes(
            Proto.CommandCode.speed_control_resp.value,
            device_id=0,
            data1=100_000,
            data2=50_000,
        )
        prot = Proto(KaitaiStream(io.BytesIO(original)))
        prot._read()

        out_io = KaitaiStream(io.BytesIO(bytes(len(original))))
        prot._io = out_io
        prot._write()
        result = bytes(out_io.to_byte_array())

        assert result[:-1] == original[:-1]
        assert result[-1] == original[-1]
