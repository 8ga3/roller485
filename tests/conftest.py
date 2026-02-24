"""共通フィクスチャ — シリアルポートをモックした Roller485Util インスタンス."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from roller485.roller485_protocol import Roller485Protocol as Proto
from roller485.util import Roller485Util


@pytest.fixture()
def mock_roller() -> Roller485Util:
    """シリアルポートを開かずに Roller485Util インスタンスを生成する.

    ``write()`` と ``read()`` は ``MagicMock`` に差し替えられるため、
    テスト側で ``side_effect`` / ``return_value`` を自由に設定できる。
    """
    with patch("serial.rs485.RS485.__init__", return_value=None):
        r = Roller485Util(target=0)
        r.write = MagicMock()  # type: ignore[assignment]
        r.read = MagicMock()  # type: ignore[assignment]
        r.is_open = True  # type: ignore[assignment]
        r.flush = MagicMock()  # type: ignore[assignment]
        r.close = MagicMock()  # type: ignore[assignment]
        return r


def build_setting_response(
    command: Proto.CommandCode,
    device_id: int = 0,
    data1: int = 0,
    data2: int = 0,
    data3: int = 0,
) -> bytes:
    """設定コマンドのレスポンスバイナリを構築する.

    レスポンスの CRC8 は magic2 バイトを除いた部分
    (cmd + dev_id + payload) から計算される。

    Args:
        command: レスポンス用の CommandCode (例: motor_switch_resp)
        device_id: デバイス ID
        data1: ペイロード data1
        data2: ペイロード data2
        data3: ペイロード data3

    Returns:
        CRC8 付きのレスポンスバイト列 (17 バイト)
    """
    import struct

    # cmd + dev_id + data1(s4le) + data2(s4le) + data3(s4le)
    body = struct.pack("<bb iii", command.value, device_id, data1, data2, data3)
    crc = Roller485Util.calculate_crc8(body)
    # AA 55 <body> <crc8>
    return b"\xaa\x55" + body + bytes([crc])


def build_readback_response(
    command: Proto.CommandCode,
    device_id: int = 0,
    *,
    payload_bytes: bytes,
) -> bytes:
    """リードバックコマンドのレスポンスバイナリを構築する.

    レスポンス構造: AA 55 <cmd> <dev_id> <payload_bytes> <crc8>
    合計 20 バイト (マジック 2 + cmd 1 + dev_id 1 + payload 15 + crc8 1)

    Args:
        command: レスポンス用 CommandCode
        device_id: デバイス ID
        payload_bytes: ペイロード部分の生バイト列 (15 バイト)

    Returns:
        CRC8 付きのレスポンスバイト列
    """
    length = Roller485Util.get_packet_length(command.value)
    frame = bytearray(length)
    frame[0] = 0xAA
    frame[1] = 0x55
    frame[2] = command.value
    frame[3] = device_id

    # ペイロード埋め込み
    payload_start = 4
    payload_end = payload_start + len(payload_bytes)
    frame[payload_start:payload_end] = payload_bytes

    # CRC8 計算 (マジック 2 バイトを除く)
    crc = Roller485Util.calculate_crc8(bytes(frame[2:-1]))
    frame[-1] = crc
    return bytes(frame)
