# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild
# type: ignore

import kaitaistruct
from kaitaistruct import ReadWriteKaitaiStruct, KaitaiStream, BytesIO
from enum import IntEnum


if getattr(kaitaistruct, 'API_VERSION', (0, 9)) < (0, 11):
    raise Exception("Incompatible Kaitai Struct Python API: 0.11 or later is required, but you have %s" % (kaitaistruct.__version__))

class Roller485Protocol(ReadWriteKaitaiStruct):
    """M5Stack Unit-Roller485用の通信プロトコルパーサーです。
    1つの定義ファイルで「送信(リクエスト)フレーム」と「返信(レスポンス)フレーム」の両方に対応しています。
    ストリームの最初のバイトを読み取り、0xAAであればレスポンスとして、そうでなければリクエストとして処理します。
    """

    class CommandCode(IntEnum):
        motor_switch = 0
        mode_setting = 1
        remove_protection = 6
        save_to_flash = 7
        encoder = 8
        button_switch_mode = 9
        rgb_led_control = 10
        rs485_baud_rate = 11
        device_id = 12
        motor_jam_protection = 13
        motor_position_over_range_protection = 14
        motor_switch_resp = 16
        mode_setting_resp = 17
        remove_protection_resp = 22
        save_to_flash_resp = 23
        encoder_resp = 24
        button_switch_mode_resp = 25
        rgb_led_control_resp = 26
        rs485_baud_rate_resp = 27
        device_id_resp = 28
        motor_jam_protection_resp = 29
        motor_position_over_range_protection_resp = 30
        speed_control = 32
        speed_pid_config = 33
        position_control = 34
        position_pid_config = 35
        current_control = 36
        speed_control_resp = 48
        speed_pid_config_resp = 49
        position_control_resp = 50
        position_pid_config_resp = 51
        current_control_resp = 52
        motor_status_readback = 64
        other_status_readback = 65
        readback_2 = 66
        readback_3 = 67
        motor_status_readback_resp = 80
        other_status_readback_resp = 81
        readback_2_resp = 82
        readback_3_resp = 83
        i2c_read_register = 96
        i2c_write_register = 97
        i2c_read_raw = 98
        i2c_write_raw = 99
        i2c_read_register_resp = 112
        i2c_write_register_resp = 113
        i2c_read_raw_resp = 114
        i2c_write_raw_resp = 115
    def __init__(self, _io=None, _parent=None, _root=None):
        super(Roller485Protocol, self).__init__(_io)
        self._parent = _parent
        self._root = _root or self

    def _read(self):
        self.first_byte = self._io.read_u1()
        if self.first_byte == 170:
            pass
            self.magic2 = self._io.read_u1()

        if self.first_byte == 170:
            pass
            self.actual_command = self._io.read_u1()

        self.device_id = self._io.read_u1()
        _on = self.command_val
        if _on == Roller485Protocol.CommandCode.i2c_read_raw:
            pass
            self.payload = Roller485Protocol.I2cReadRawReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_read_raw_resp:
            pass
            self.payload = Roller485Protocol.I2cReadRegResp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_read_register:
            pass
            self.payload = Roller485Protocol.I2cReadRegReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_read_register_resp:
            pass
            self.payload = Roller485Protocol.I2cReadRegResp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw:
            pass
            self.payload = Roller485Protocol.I2cWriteRawReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw_resp:
            pass
            self.payload = Roller485Protocol.WriteStatusResp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_write_register:
            pass
            self.payload = Roller485Protocol.I2cWriteRegReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.i2c_write_register_resp:
            pass
            self.payload = Roller485Protocol.WriteStatusResp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.motor_status_readback:
            pass
            self.payload = Roller485Protocol.ReadbackReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.motor_status_readback_resp:
            pass
            self.payload = Roller485Protocol.MotorStatusResp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.other_status_readback:
            pass
            self.payload = Roller485Protocol.ReadbackReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.other_status_readback_resp:
            pass
            self.payload = Roller485Protocol.OtherStatusResp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.readback_2:
            pass
            self.payload = Roller485Protocol.ReadbackReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.readback_2_resp:
            pass
            self.payload = Roller485Protocol.Readback2Resp(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.readback_3:
            pass
            self.payload = Roller485Protocol.ReadbackReq(self._io, self, self._root)
            self.payload._read()
        elif _on == Roller485Protocol.CommandCode.readback_3_resp:
            pass
            self.payload = Roller485Protocol.Readback3Resp(self._io, self, self._root)
            self.payload._read()
        else:
            pass
            self.payload = Roller485Protocol.ConfigPayload(self._io, self, self._root)
            self.payload._read()
        self.crc8 = self._io.read_u1()
        self._dirty = False


    def _fetch_instances(self):
        pass
        if self.first_byte == 170:
            pass

        if self.first_byte == 170:
            pass

        _on = self.command_val
        if _on == Roller485Protocol.CommandCode.i2c_read_raw:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_read_raw_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_read_register:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_read_register_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_write_register:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.i2c_write_register_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.motor_status_readback:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.motor_status_readback_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.other_status_readback:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.other_status_readback_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.readback_2:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.readback_2_resp:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.readback_3:
            pass
            self.payload._fetch_instances()
        elif _on == Roller485Protocol.CommandCode.readback_3_resp:
            pass
            self.payload._fetch_instances()
        else:
            pass
            self.payload._fetch_instances()


    def _write__seq(self, io=None):
        super(Roller485Protocol, self)._write__seq(io)
        self._io.write_u1(self.first_byte)
        if self.first_byte == 170:
            pass
            self._io.write_u1(self.magic2)

        if self.first_byte == 170:
            pass
            self._io.write_u1(self.actual_command)

        self._io.write_u1(self.device_id)
        _on = self.command_val
        if _on == Roller485Protocol.CommandCode.i2c_read_raw:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_read_raw_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_read_register:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_read_register_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_write_register:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.i2c_write_register_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.motor_status_readback:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.motor_status_readback_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.other_status_readback:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.other_status_readback_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.readback_2:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.readback_2_resp:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.readback_3:
            pass
            self.payload._write__seq(self._io)
        elif _on == Roller485Protocol.CommandCode.readback_3_resp:
            pass
            self.payload._write__seq(self._io)
        else:
            pass
            self.payload._write__seq(self._io)
        self._io.write_u1(self.crc8)


    def _check(self):
        if self.first_byte == 170:
            pass

        if self.first_byte == 170:
            pass

        _on = self.command_val
        if _on == Roller485Protocol.CommandCode.i2c_read_raw:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_read_raw_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_read_register:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_read_register_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_write_raw_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_write_register:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.i2c_write_register_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.motor_status_readback:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.motor_status_readback_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.other_status_readback:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.other_status_readback_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.readback_2:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.readback_2_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.readback_3:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        elif _on == Roller485Protocol.CommandCode.readback_3_resp:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        else:
            pass
            if self.payload._root != self._root:
                raise kaitaistruct.ConsistencyError(u"payload", self._root, self.payload._root)
            if self.payload._parent != self:
                raise kaitaistruct.ConsistencyError(u"payload", self, self.payload._parent)
        self._dirty = False

    class ConfigPayload(ReadWriteKaitaiStruct):
        """各種設定・制御コマンドの送受信で使われる標準的な12バイトのペイロード."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.ConfigPayload, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.data1 = self._io.read_s4le()
            self.data2 = self._io.read_s4le()
            self.data3 = self._io.read_s4le()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.ConfigPayload, self)._write__seq(io)
            self._io.write_s4le(self.data1)
            self._io.write_s4le(self.data2)
            self._io.write_s4le(self.data3)


        def _check(self):
            self._dirty = False


    class I2cReadRawReq(ReadWriteKaitaiStruct):
        """0x62 I2C Read Raw リクエストペイロード (2バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.I2cReadRawReq, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.i2c_address = self._io.read_u1()
            self.data_length = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.I2cReadRawReq, self)._write__seq(io)
            self._io.write_u1(self.i2c_address)
            self._io.write_u1(self.data_length)


        def _check(self):
            self._dirty = False


    class I2cReadRegReq(ReadWriteKaitaiStruct):
        """0x60 I2C Register Read リクエストペイロード (5バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.I2cReadRegReq, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.i2c_address = self._io.read_u1()
            self.register_address_length = self._io.read_u1()
            self.register_address = self._io.read_u2le()
            self.data_length = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.I2cReadRegReq, self)._write__seq(io)
            self._io.write_u1(self.i2c_address)
            self._io.write_u1(self.register_address_length)
            self._io.write_u2le(self.register_address)
            self._io.write_u1(self.data_length)


        def _check(self):
            self._dirty = False


    class I2cReadRegResp(ReadWriteKaitaiStruct):
        """0x70 / 0x72 I2C Read レスポンスペイロード (22バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.I2cReadRegResp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.read_status = self._io.read_u1()
            self.reserve1 = self._io.read_u1()
            self.data_length = self._io.read_u1()
            self.reserve2 = self._io.read_bytes(3)
            self.data = self._io.read_bytes(16)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.I2cReadRegResp, self)._write__seq(io)
            self._io.write_u1(self.read_status)
            self._io.write_u1(self.reserve1)
            self._io.write_u1(self.data_length)
            self._io.write_bytes(self.reserve2)
            self._io.write_bytes(self.data)


        def _check(self):
            if len(self.reserve2) != 3:
                raise kaitaistruct.ConsistencyError(u"reserve2", 3, len(self.reserve2))
            if len(self.data) != 16:
                raise kaitaistruct.ConsistencyError(u"data", 16, len(self.data))
            self._dirty = False


    class I2cWriteRawReq(ReadWriteKaitaiStruct):
        """0x63 I2C Write Raw リクエストペイロード (22バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.I2cWriteRawReq, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.i2c_address = self._io.read_u1()
            self.data_length = self._io.read_u1()
            self.stop_bit = self._io.read_u1()
            self.reserve = self._io.read_bytes(3)
            self.data = self._io.read_bytes(16)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.I2cWriteRawReq, self)._write__seq(io)
            self._io.write_u1(self.i2c_address)
            self._io.write_u1(self.data_length)
            self._io.write_u1(self.stop_bit)
            self._io.write_bytes(self.reserve)
            self._io.write_bytes(self.data)


        def _check(self):
            if len(self.reserve) != 3:
                raise kaitaistruct.ConsistencyError(u"reserve", 3, len(self.reserve))
            if len(self.data) != 16:
                raise kaitaistruct.ConsistencyError(u"data", 16, len(self.data))
            self._dirty = False


    class I2cWriteRegReq(ReadWriteKaitaiStruct):
        """0x61 I2C Register Write リクエストペイロード (24バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.I2cWriteRegReq, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.i2c_address = self._io.read_u1()
            self.register_address_length = self._io.read_u1()
            self.register_address = self._io.read_u2le()
            self.data_length = self._io.read_u1()
            self.reserve = self._io.read_bytes(3)
            self.data = self._io.read_bytes(16)
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.I2cWriteRegReq, self)._write__seq(io)
            self._io.write_u1(self.i2c_address)
            self._io.write_u1(self.register_address_length)
            self._io.write_u2le(self.register_address)
            self._io.write_u1(self.data_length)
            self._io.write_bytes(self.reserve)
            self._io.write_bytes(self.data)


        def _check(self):
            if len(self.reserve) != 3:
                raise kaitaistruct.ConsistencyError(u"reserve", 3, len(self.reserve))
            if len(self.data) != 16:
                raise kaitaistruct.ConsistencyError(u"data", 16, len(self.data))
            self._dirty = False


    class MotorStatusResp(ReadWriteKaitaiStruct):
        """0x50 Motor Status Readback レスポンスペイロード (15バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.MotorStatusResp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.speed = self._io.read_s4le()
            self.position = self._io.read_s4le()
            self.current = self._io.read_s4le()
            self.mode = self._io.read_u1()
            self.status = self._io.read_u1()
            self.error = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.MotorStatusResp, self)._write__seq(io)
            self._io.write_s4le(self.speed)
            self._io.write_s4le(self.position)
            self._io.write_s4le(self.current)
            self._io.write_u1(self.mode)
            self._io.write_u1(self.status)
            self._io.write_u1(self.error)


        def _check(self):
            self._dirty = False


    class OtherStatusResp(ReadWriteKaitaiStruct):
        """0x51 Other Status Readback レスポンスペイロード (15バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.OtherStatusResp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.vin_x100 = self._io.read_u4le()
            self.temp = self._io.read_s4le()
            self.encoder_counter = self._io.read_s4le()
            self.rgb_mode = self._io.read_u1()
            self.rgb_brightness = self._io.read_u1()
            self.reserve = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.OtherStatusResp, self)._write__seq(io)
            self._io.write_u4le(self.vin_x100)
            self._io.write_s4le(self.temp)
            self._io.write_s4le(self.encoder_counter)
            self._io.write_u1(self.rgb_mode)
            self._io.write_u1(self.rgb_brightness)
            self._io.write_u1(self.reserve)


        def _check(self):
            self._dirty = False


    class Readback2Resp(ReadWriteKaitaiStruct):
        """0x52 Readback 2 レスポンスペイロード (15バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.Readback2Resp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.speed_p = self._io.read_u4le()
            self.speed_i = self._io.read_u4le()
            self.speed_d = self._io.read_u4le()
            self.rgb_b = self._io.read_u1()
            self.rgb_g = self._io.read_u1()
            self.rgb_r = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.Readback2Resp, self)._write__seq(io)
            self._io.write_u4le(self.speed_p)
            self._io.write_u4le(self.speed_i)
            self._io.write_u4le(self.speed_d)
            self._io.write_u1(self.rgb_b)
            self._io.write_u1(self.rgb_g)
            self._io.write_u1(self.rgb_r)


        def _check(self):
            self._dirty = False


    class Readback3Resp(ReadWriteKaitaiStruct):
        """0x53 Readback 3 レスポンスペイロード (15バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.Readback3Resp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.position_p = self._io.read_u4le()
            self.position_i = self._io.read_u4le()
            self.position_d = self._io.read_u4le()
            self.rs485_id = self._io.read_u1()
            self.rs485_bps = self._io.read_u1()
            self.button_switch_mode = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.Readback3Resp, self)._write__seq(io)
            self._io.write_u4le(self.position_p)
            self._io.write_u4le(self.position_i)
            self._io.write_u4le(self.position_d)
            self._io.write_u1(self.rs485_id)
            self._io.write_u1(self.rs485_bps)
            self._io.write_u1(self.button_switch_mode)


        def _check(self):
            self._dirty = False


    class ReadbackReq(ReadWriteKaitaiStruct):
        """ステータス読み出しのリクエストペイロード (1バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.ReadbackReq, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.read_flag = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.ReadbackReq, self)._write__seq(io)
            self._io.write_u1(self.read_flag)


        def _check(self):
            self._dirty = False


    class WriteStatusResp(ReadWriteKaitaiStruct):
        """0x71 / 0x73 I2C Write レスポンスペイロード (1バイト)."""
        def __init__(self, _io=None, _parent=None, _root=None):
            super(Roller485Protocol.WriteStatusResp, self).__init__(_io)
            self._parent = _parent
            self._root = _root

        def _read(self):
            self.write_status = self._io.read_u1()
            self._dirty = False


        def _fetch_instances(self):
            pass


        def _write__seq(self, io=None):
            super(Roller485Protocol.WriteStatusResp, self)._write__seq(io)
            self._io.write_u1(self.write_status)


        def _check(self):
            self._dirty = False


    @property
    def command_val(self):
        """判定結果に基づく実際のコマンド値."""
        if hasattr(self, '_m_command_val'):
            return self._m_command_val

        self._m_command_val = KaitaiStream.resolve_enum(Roller485Protocol.CommandCode, (self.actual_command if self.is_response else self.first_byte))
        return getattr(self, '_m_command_val', None)

    def _invalidate_command_val(self):
        del self._m_command_val
    @property
    def is_response(self):
        """このフレームがデバイスからのレスポンス（返信）かどうかを判定します."""
        if hasattr(self, '_m_is_response'):
            return self._m_is_response

        self._m_is_response = self.first_byte == 170
        return getattr(self, '_m_is_response', None)

    def _invalidate_is_response(self):
        del self._m_is_response

