meta:
  id: unit_roller485_response
  title: M5Stack Unit-Roller485 RS485 Response Protocol
  endian: le

doc: |
  M5Stack Unit-Roller485用の通信プロトコル（レスポンスフレーム用）パーサーです。
  すべての返信メッセージの先頭に付与されるマジックナンバー(0xAA 0x55)が含まれています。

seq:
  - id: magic
    contents: [0xaa, 0x55]
    doc: レスポンスフレーム開始のマジックナンバー。CRC計算には含まれません。
  - id: command
    type: u1
    enum: command_code
    doc: レスポンスのコマンドコード
  - id: device_id
    type: u1
    doc: デバイスアドレス（デフォルトは0x00）
  - id: payload
    type:
      switch-on: command
      cases:
        'command_code::motor_status_readback_resp': motor_status_resp
        'command_code::other_status_readback_resp': other_status_resp
        'command_code::readback_2_resp': readback_2_resp
        'command_code::readback_3_resp': readback_3_resp
        'command_code::i2c_read_register_resp': i2c_read_reg_resp
        'command_code::i2c_write_register_resp': write_status_resp
        'command_code::i2c_read_raw_resp': i2c_read_reg_resp
        'command_code::i2c_write_raw_resp': write_status_resp
        _: config_payload
  - id: crc8
    type: u1
    doc: Commandバイトからペイロードの末尾までのCRC8チェックサム

types:
  config_payload:
    doc: 各種設定コマンドのレスポンスで使われる標準的な12バイトのペイロード。
    seq:
      - id: data1
        size: 4
      - id: data2
        size: 4
      - id: data3
        size: 4

  motor_status_resp:
    doc: 0x50 Motor Status Readback レスポンス (15バイト)
    seq:
      - id: speed
        type: s4
      - id: position
        type: s4
      - id: current
        type: s4
      - id: mode
        type: u1
      - id: status
        type: u1
      - id: error
        type: u1

  other_status_resp:
    doc: 0x51 Other Status Readback レスポンス (15バイト)
    seq:
      - id: vin_x100
        type: u4
      - id: temp
        type: s4
      - id: encoder_counter
        type: s4
      - id: rgb_mode
        type: u1
      - id: rgb_brightness
        type: u1
      - id: reserve
        type: u1

  readback_2_resp:
    doc: 0x52 Readback 2 レスポンス (15バイト)
    seq:
      - id: speed_p
        type: u4
      - id: speed_i
        type: u4
      - id: speed_d
        type: u4
      - id: rgb_b
        type: u1
      - id: rgb_g
        type: u1
      - id: rgb_r
        type: u1

  readback_3_resp:
    doc: 0x53 Readback 3 レスポンス (15バイト)
    seq:
      - id: position_p
        type: u4
      - id: position_i
        type: u4
      - id: position_d
        type: u4
      - id: rs485_id
        type: u1
      - id: rs485_bps
        type: u1
      - id: button_switch_mode
        type: u1

  i2c_read_reg_resp:
    doc: 0x70 / 0x72 I2C Read レスポンス (22バイト)
    seq:
      - id: read_status
        type: u1
      - id: reserve1
        type: u1
      - id: data_length
        type: u1
      - id: reserve2
        size: 3
      - id: data
        size: 16

  write_status_resp:
    doc: 0x71 / 0x73 I2C Write レスポンス (1バイト)
    seq:
      - id: write_status
        type: u1

enums:
  command_code:
    # 構成コマンドのレスポンス
    0x10: motor_switch_resp
    0x11: mode_setting_resp
    0x16: remove_protection_resp
    0x17: save_to_flash_resp
    0x18: encoder_resp
    0x19: button_switch_mode_resp
    0x1A: rgb_led_control_resp
    0x1B: rs485_baud_rate_resp
    0x1C: device_id_resp
    0x1D: motor_jam_protection_resp
    0x1E: motor_position_over_range_protection_resp
    # ループ制御系のレスポンス
    0x30: speed_control_resp
    0x31: speed_pid_config_resp
    0x32: position_control_resp
    0x33: position_pid_config_resp
    0x34: current_control_resp
    # ステータス読み出しのレスポンス
    0x50: motor_status_readback_resp
    0x51: other_status_readback_resp
    0x52: readback_2_resp
    0x53: readback_3_resp
    # I2C制御系のレスポンス
    0x70: i2c_read_register_resp
    0x71: i2c_write_register_resp
    0x72: i2c_read_raw_resp
    0x73: i2c_write_raw_resp
