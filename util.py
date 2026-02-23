import io
import time
from enum import IntEnum

import serial.rs485 as rs
from kaitaistruct import KaitaiStream

from roller485_protocol import Roller485Protocol as Proto


class Roller485Util(rs.RS485):
    def __init__(self, target: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target = target

    @classmethod
    def calculate_crc8(cls, data: bytes) -> int:
        """Unit-Roller485用のCRC8チェックサムを計算します。

        Args:
            data (bytes): CRC計算対象のバイトデータ

        Returns:
            int: 計算されたCRC8値 (0〜255)
        """
        crc = 0x00

        for byte in data:
            crc ^= byte
            for _ in range(8):
                if crc & 0x01:
                    crc = (crc >> 1) ^ 0x8C
                else:
                    crc >>= 1

        return crc

    @classmethod
    def get_packet_length(cls, command_code: int) -> int:
        """コマンドコードからパケットの総バイト数

        コマンドコードからパケットの総バイト数（受信時のマジックナンバー2バイト分を含む）を取得します。

        Args:
            command_code (int): コマンドコード

        Returns:
            int: パケットの総バイト数
        """
        # 特殊な長さを持つパケットのマップ
        length_map = {
            # --- ステータス読み出し (リクエスト: 4バイト) ---
            0x40: 4,
            0x41: 4,
            0x42: 4,
            0x43: 4,
            # --- ステータス読み出し (レスポンス: 18 + マジック2 = 20バイト) ---
            0x50: 20,
            0x51: 20,
            0x52: 20,
            0x53: 20,
            # --- I2C転送コマンド (リクエスト) ---
            0x60: 8,  # I2C Read Reg Req
            0x61: 25,  # I2C Write Reg Req
            0x62: 5,  # I2C Read Raw Req
            0x63: 25,  # I2C Write Raw Req
            # --- I2C転送コマンド (レスポンス: ペイロード + マジック2バイト) ---
            0x70: 27,  # I2C Read Reg Resp (25 + 2)
            0x71: 6,  # I2C Write Reg Resp (4 + 2)
            0x72: 27,  # I2C Read Raw Resp (25 + 2)
            0x73: 6,  # I2C Write Raw Resp (4 + 2)
        }

        # 辞書に存在すればそのサイズを返す
        if command_code in length_map:
            return length_map[command_code]

        # --- 上記以外の標準コマンド (設定・ループ制御など) ---

        # レスポンスのコマンドコード (0x10〜0x1E, 0x30〜0x34 等)
        # ベースの15バイト + マジックナンバーの2バイト = 17バイト
        if (0x10 <= command_code <= 0x1E) or (0x30 <= command_code <= 0x34):
            return 17

        # リクエストのコマンドコード (0x00〜0x0E, 0x20〜0x24 等)
        # 15バイト固定
        return 15

    @classmethod
    def replace_crc8(cls, prot: Proto) -> None:
        """CRC8を計算しパケットの末尾に代入

        Args:
            prot (Proto): CRC8を計算する対象のプロトコルオブジェクト
        """
        output = prot._io.to_byte_array()
        prot.crc8 = cls.calculate_crc8(output[:-1])
        prot._io.seek(prot._io.pos() - 1)
        binary = prot.crc8.to_bytes(1, "little")
        prot._io.write_bytes(binary)

    def _delay(self):
        time.sleep(0.05)

    class Switch(IntEnum):
        Off = 0
        On = 1

    def _setting(
        self, command: Proto.CommandCode, data1: int, data2: int = 0, data3: int = 0
    ) -> None:
        """設定コマンドを送信

        Args:
            command (Proto.CommandCode): 設定するコマンド
            data1 (int): データ1
            data2 (int, optional): データ2. Defaults to 0.
            data3 (int, optional): データ3. Defaults to 0.
        """
        length = self.get_packet_length(command.value)
        _io = KaitaiStream(io.BytesIO(bytes(length)))

        prot = Proto(_io)
        prot.first_byte = command
        prot.device_id = self.target
        prot.crc8 = 0  # 後で正しい値を計算

        payload = Proto.ConfigPayload(None, prot, prot._root)
        payload.data1 = data1
        payload.data2 = data2
        payload.data3 = data3
        payload._check()

        prot.payload = payload
        prot._check()

        prot._write()

        self.replace_crc8(prot)
        output = _io.to_byte_array()
        self.write(output)

    def _setting_resp(
        self, command: Proto.CommandCode, data1: int = 0, data2: int = 0, data3: int = 0
    ) -> bool:
        """設定コマンドのレスポンスを確認

        Args:
            command (Proto.CommandCode): 設定したコマンド
            data1 (int, optional): データ1. Defaults to 0.
            data2 (int, optional): データ2. Defaults to 0.
            data3 (int, optional): データ3. Defaults to 0.

        Returns:
            bool: レスポンスが期待通りかどうか
        """
        msg = self.read(self.get_packet_length(command.value))
        resp = Proto(KaitaiStream(io.BytesIO(msg)))
        resp._read()
        crc8 = self.calculate_crc8(msg[2:-1])
        if crc8 != resp.crc8:
            return False
        return (
            resp.payload.data1 == data1
            and resp.payload.data2 == data2
            and resp.payload.data3 == data3
        )

    def motor_switch(self, state: Switch) -> bool:
        """モーターON/OFF

        Args:
            state (Switch): 1でON、0でOFF
        """
        self._setting(Proto.CommandCode.motor_switch, data1=state.value)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.motor_switch_resp, data1=state.value
        )

    class MotorMode(IntEnum):
        Speed = 1
        Position = 2
        Current = 3
        Encoder = 4

    def mode_setting(self, mode: MotorMode) -> None:
        """モード設定

        フラッシュに保存されます。

        Args:
            mode (MotorMode): 設定するモード
        """
        self._setting(Proto.CommandCode.mode_setting, data1=mode.value)
        self._delay()
        return self._setting_resp(Proto.CommandCode.mode_setting_resp, data1=mode.value)

    def remove_protection(self, status: int) -> None:
        """保護解除

        Args:
            status (int): 保護解除のステータス
        """
        status = max(0, min(255, status))
        self._setting(Proto.CommandCode.remove_protection, data2=status)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.remove_protection_resp, data2=status
        )

    def save_to_flash(self) -> None:
        """フラッシュメモリに保存"""
        self._setting(Proto.CommandCode.save_to_flash, data1=1)
        self._delay()
        return self._setting_resp(Proto.CommandCode.save_to_flash_resp, data1=1)

    def set_encoder(self, value: int) -> None:
        """エンコーダの設定

        Args:
            value (int): エンコーダの値
        """
        self._setting(Proto.CommandCode.encoder, data1=value)
        self._delay()
        return self._setting_resp(Proto.CommandCode.encoder_resp, data1=value)

    class ButtonMode(IntEnum):
        Off = 0
        On = 1  # Press and hold for 5S to switch modes in running mode.

    def button_switching_mode(self, mode: ButtonMode) -> None:
        """ボタンの切り替えモード設定

        Args:
            mode (ButtonMode): 設定するモード
        """
        self._setting(Proto.CommandCode.button_switch_mode, data1=mode.value)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.button_switch_mode_resp, data1=mode.value
        )

    def rgb_led_control(
        self,
        r: int = 0,
        g: int = 0,
        b: int = 0,
        mode: int = 0,
        brightness: int = 100,
    ) -> None:
        """LEDの制御

        フラッシュに保存されます。

        Args:
            r (int, optional): 赤の値. Defaults to 0.
            g (int, optional): 緑の値. Defaults to 0.
            b (int, optional): 青の値. Defaults to 0.
            mode (int, optional): モード. Defaults to 0. 0: Default system state display, 1: User-defined control
            brightness (int, optional): 明るさ(0〜100). Defaults to 100.
        """
        # RGB値を0〜255にクリップ
        r = max(0, min(255, r))
        g = max(0, min(255, g))
        b = max(0, min(255, b))
        mode = max(0, min(1, mode))
        brightness = max(0, min(100, brightness))
        data1 = r + g * 256 + b * 256 * 256 + mode * 256 * 256 * 256
        data2 = brightness
        self._setting(Proto.CommandCode.rgb_led_control, data1=data1, data2=data2)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.rgb_led_control_resp, data1=data1, data2=data2
        )

    class RS485BaudRate(IntEnum):
        Baud115200 = 0
        Baud19200 = 1
        Baud9600 = 2

    def set_rs485_baud_rate(self, baud_rate: RS485BaudRate) -> None:
        """RS485のボーレート設定

        フラッシュに保存されます。

        Args:
            baud_rate (RS485BaudRate): 設定するボーレート
        """
        self._setting(Proto.CommandCode.rs485_baud_rate, data1=baud_rate.value)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.rs485_baud_rate_resp, data1=baud_rate.value
        )

    def set_device_id(self, device_id: int) -> None:
        """デバイスIDの設定

        フラッシュに保存されます。

        Args:
            device_id (int): 設定するデバイスID
        """
        device_id = max(0, min(255, device_id))
        self._setting(Proto.CommandCode.device_id, data1=device_id)
        self._delay()
        return self._setting_resp(Proto.CommandCode.device_id_resp, data1=device_id)

    def set_motor_jam_protection(self, enable: bool) -> None:
        """モータジャム保護の設定

        Args:
            enable (bool): False: 無効, True: 有効
        """
        enable = 1 if enable else 0
        self._setting(Proto.CommandCode.motor_jam_protection, data1=enable)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.motor_jam_protection_resp, data1=enable
        )

    def set_motor_position_over_range_protection(self, enable: bool) -> None:
        """モータ位置オーバーレンジ保護の設定

        スピードモード設定

        フラッシュに保存されます。

        Args:
            enable (bool): False: 無効, True: 有効
        """
        enable = 1 if enable else 0
        self._setting(
            Proto.CommandCode.motor_position_over_range_protection, data1=enable
        )
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.motor_position_over_range_protection_resp, data1=enable
        )

    def set_speed_and_max_current(self, speed: int, max_current: float) -> None:
        """モータ速度と最大電流の設定

        スピードモード設定

        Args:
            speed (int): 設定する速度 (-21000000-21000000) [RPM]
            max_current (float): 設定する最大電流 (-1200-1200) [mA]
        """
        speed = max(-21_000_000, min(21_000_000, speed)) * 100
        max_current_int: int = int(max(-1200, min(1200, max_current))) * 100
        self._setting(
            Proto.CommandCode.speed_control, data1=speed, data2=max_current_int
        )
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.speed_control_resp,
            data1=speed,
            data2=max_current_int,
        )

    def set_speed_pid(self, p: float, i: float, d: float) -> None:
        """モータ速度PIDの設定

        スピードモード設定

        フラッシュに保存されます。

        Args:
            p (float): 設定するP値
            i (float): 設定するI値
            d (float): 設定するD値
        """
        int_p: int = int(p * 100_000)
        int_i: int = int(i * 100_000)
        int_d: int = int(d * 100_000)
        self._setting(
            Proto.CommandCode.speed_pid_config, data1=int_p, data2=int_i, data3=int_d
        )
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.speed_pid_config_resp,
            data1=int_p,
            data2=int_i,
            data3=int_d,
        )

    def set_position_and_max_current(self, position: int, max_current: float) -> None:
        """モータ位置と最大電流の設定

        ポジションモード設定

        Args:
            position (int): 設定する位置 (-21000000-21000000) [counts]
            max_current (float): 設定する最大電流 (-1200-1200) [mA]
        """
        position = max(-21_000_000, min(21_000_000, position)) * 100
        max_current_int: int = int(max(-1200, min(1200, max_current))) * 100
        self._setting(
            Proto.CommandCode.position_control,
            data1=position,
            data2=max_current_int,
        )
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.position_control_resp,
            data1=position,
            data2=max_current_int,
        )

    def set_position_pid(self, p: float, i: float, d: float) -> None:
        """モータ位置PIDの設定

        ポジションモード設定

        フラッシュに保存されます。

        Args:
            p (float): 設定するP値
            i (float): 設定するI値
            d (float): 設定するD値
        """
        int_p: int = int(p * 100_000)
        int_i: int = int(i * 100_000)
        int_d: int = int(d * 100_000)
        self._setting(
            Proto.CommandCode.position_pid_config, data1=int_p, data2=int_i, data3=int_d
        )
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.position_pid_config_resp,
            data1=int_p,
            data2=int_i,
            data3=int_d,
        )

    def set_current(self, current: float) -> None:
        """モータ電流の設定

        電流モード設定

        Args:
            current (float): 設定する電流 (-1200-1200) [mA]
        """
        current_int: int = int(max(-1200, min(1200, current)) * 100)
        self._setting(Proto.CommandCode.current_control, data1=current_int)
        self._delay()
        return self._setting_resp(
            Proto.CommandCode.current_control_resp, data1=current_int
        )

    def _send_readback(self, command: Proto.CommandCode, read_flag: int = 0) -> None:
        length = self.get_packet_length(command.value)
        _io = KaitaiStream(io.BytesIO(bytes(length)))

        prot = Proto(_io)
        prot.first_byte = command
        prot.device_id = self.target
        prot.crc8 = 0  # 後で正しい値を計算

        payload = Proto.ReadbackReq(None, prot, prot._root)
        payload.read_flag = read_flag
        payload._check()

        prot.payload = payload
        prot._check()

        prot._write()

        self.replace_crc8(prot)
        output = _io.to_byte_array()
        self.write(output)

    def get_motor_status(self) -> dict:
        """モータの状態を読み取る

        Args:
            dict
        """
        self._send_readback(Proto.CommandCode.motor_status_readback)
        self._delay()

        msg = self.read(
            self.get_packet_length(Proto.CommandCode.motor_status_readback.value)
        )
        resp = Proto(KaitaiStream(io.BytesIO(msg)))
        resp._read()
        crc8 = self.calculate_crc8(msg[2:-1])
        if crc8 != resp.crc8:
            return {}
        return {
            "speed": resp.payload.speed / 100,
            "position": resp.payload.position / 100,
            "current": resp.payload.current / 100,
            "mode": resp.payload.mode,
            "status": resp.payload.status,
            "error": resp.payload.error,
        }

    def get_other_status(self) -> dict:
        """その他の状態を読み取る

        Args:
            dict
        """
        self._send_readback(Proto.CommandCode.other_status_readback)
        self._delay()

        msg = self.read(
            self.get_packet_length(Proto.CommandCode.other_status_readback.value)
        )
        resp = Proto(KaitaiStream(io.BytesIO(msg)))
        resp._read()
        crc8 = self.calculate_crc8(msg[2:-1])
        if crc8 != resp.crc8:
            return {}
        return {
            "vin": resp.payload.vin_x100 / 100,
            "temp": resp.payload.temp,
            "encoder_counter": resp.payload.encoder_counter,
            "rgb_mode": resp.payload.rgb_mode,
            "rgb_brightness": resp.payload.rgb_brightness,
        }

    def get_speed_pid_and_rgb(self) -> dict:
        """PIDとRGBの状態を読み取る

        Args:
            dict
        """
        self._send_readback(Proto.CommandCode.readback_2)
        self._delay()

        msg = self.read(self.get_packet_length(Proto.CommandCode.readback_2_resp.value))
        resp = Proto(KaitaiStream(io.BytesIO(msg)))
        resp._read()
        crc8 = self.calculate_crc8(msg[2:-1])
        if crc8 != resp.crc8:
            return {}
        return {
            "speed_p": resp.payload.speed_p / 100_000,
            "speed_i": resp.payload.speed_i / 100_000,
            "speed_d": resp.payload.speed_d / 100_000,
            "rgb_b": resp.payload.rgb_b,
            "rgb_g": resp.payload.rgb_g,
            "rgb_r": resp.payload.rgb_r,
        }

    def get_position_pid_and_other(self) -> dict:
        """位置とIDの状態を読み取る

        Args:
            dict
        """
        self._send_readback(Proto.CommandCode.readback_3)
        self._delay()

        msg = self.read(self.get_packet_length(Proto.CommandCode.readback_3_resp.value))
        resp = Proto(KaitaiStream(io.BytesIO(msg)))
        resp._read()
        crc8 = self.calculate_crc8(msg[2:-1])
        if crc8 != resp.crc8:
            return {}
        return {
            "position_p": resp.payload.position_p / 100_000,
            "position_i": resp.payload.position_i / 100_000,
            "position_d": resp.payload.position_d / 100_000,
            "rs485_id": resp.payload.rs485_id,
            "rs485_bps": resp.payload.rs485_bps,
            "button_switch_mode": resp.payload.button_switch_mode,
        }
