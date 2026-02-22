meta:
  id: unit_roller485_protocol
  title: M5Stack Unit-Roller485 RS485 Protocol (Requests and Responses)
  endian: le

doc: |
  M5Stack Unit-Roller485用の通信プロトコルパーサーです。
  1つの定義ファイルで「送信(リクエスト)フレーム」と「返信(レスポンス)フレーム」の両方に対応しています。
  ストリームの最初のバイトを読み取り、0xAAであればレスポンスとして、そうでなければリクエストとして処理します。

seq:
  - id: first_byte
    type: u1
    doc: マジックナンバーの先頭バイト(0xAA)、または送信時のコマンドコード

  - id: magic2
    type: u1
    if: first_byte == 0xaa
    doc: レスポンスフレームの場合のみ存在するマジックナンバーの2バイト目(0x55)

  - id: actual_command
    type: u1
    if: first_byte == 0xaa
    doc: レスポンスフレームの場合の実際のコマンドコード

  - id: device_id
    type: u1
    doc: デバイスアドレス（デフォルトは0x00）

  - id: payload
    type:
      switch-on: command_val
      cases:
        # --- Readback Command (送信) ---
        'command_code::motor_status_readback': readback_req
        'command_code::other_status_readback': readback_req
        'command_code::readback_2': readback_req
        'command_code::readback_3': readback_req

        # --- Readback Command (受信) ---
        'command_code::motor_status_readback_resp': motor_status_resp
        'command_code::other_status_readback_resp': other_status_resp
        'command_code::readback_2_resp': readback_2_resp
        'command_code::readback_3_resp': readback_3_resp

        # --- I2C Forwarding Command (送信) ---
        'command_code::i2c_read_register': i2c_read_reg_req
        'command_code::i2c_write_register': i2c_write_reg_req
        'command_code::i2c_read_raw': i2c_read_raw_req
        'command_code::i2c_write_raw': i2c_write_raw_req

        # --- I2C Forwarding Command (受信) ---
        'command_code::i2c_read_register_resp': i2c_read_reg_resp
        'command_code::i2c_write_register_resp': write_status_resp
        'command_code::i2c_read_raw_resp': i2c_read_reg_resp
        'command_code::i2c_write_raw_resp': write_status_resp

        # デフォルト (設定・制御コマンド等の12バイト固定フォーマット)
        _: config_payload

  - id: crc8
    type: u1
    doc: Commandバイトからペイロードの末尾までのCRC8チェックサム

instances:
  is_response:
    value: first_byte == 0xaa
    doc: このフレームがデバイスからのレスポンス（返信）かどうかを判定します
  command_val:
    value: 'is_response ? actual_command : first_byte'
    enum: command_code
    doc: 判定結果に基づく実際のコマンド値

types:
  config_payload:
    doc: 各種設定・制御コマンドの送受信で使われる標準的な12バイトのペイロード
    seq:
      - id: data1
        type: s4
      - id: data2
        type: s4
      - id: data3
        type: s4

  readback_req:
    doc: ステータス読み出しのリクエストペイロード (1バイト)
    seq:
      - id: read_flag
        type: u1

  motor_status_resp:
    doc: 0x50 Motor Status Readback レスポンスペイロード (15バイト)
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
    doc: 0x51 Other Status Readback レスポンスペイロード (15バイト)
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
    doc: 0x52 Readback 2 レスポンスペイロード (15バイト)
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
    doc: 0x53 Readback 3 レスポンスペイロード (15バイト)
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

  i2c_read_reg_req:
    doc: 0x60 I2C Register Read リクエストペイロード (5バイト)
    seq:
      - id: i2c_address
        type: u1
      - id: register_address_length
        type: u1
      - id: register_address
        type: u2
      - id: data_length
        type: u1

  i2c_read_reg_resp:
    doc: 0x70 / 0x72 I2C Read レスポンスペイロード (22バイト)
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

  i2c_write_reg_req:
    doc: 0x61 I2C Register Write リクエストペイロード (24バイト)
    seq:
      - id: i2c_address
        type: u1
      - id: register_address_length
        type: u1
      - id: register_address
        type: u2
      - id: data_length
        type: u1
      - id: reserve
        size: 3
      - id: data
        size: 16

  write_status_resp:
    doc: 0x71 / 0x73 I2C Write レスポンスペイロード (1バイト)
    seq:
      - id: write_status
        type: u1

  i2c_read_raw_req:
    doc: 0x62 I2C Read Raw リクエストペイロード (2バイト)
    seq:
      - id: i2c_address
        type: u1
      - id: data_length
        type: u1

  i2c_write_raw_req:
    doc: 0x63 I2C Write Raw リクエストペイロード (22バイト)
    seq:
      - id: i2c_address
        type: u1
      - id: data_length
        type: u1
      - id: stop_bit
        type: u1
      - id: reserve
        size: 3
      - id: data
        size: 16

enums:
  command_code:
    # --- Configuration Command Set ---
    0x00: motor_switch
    0x10: motor_switch_resp
    0x01: mode_setting
    0x11: mode_setting_resp
    0x06: remove_protection
    0x16: remove_protection_resp
    0x07: save_to_flash
    0x17: save_to_flash_resp
    0x08: encoder
    0x18: encoder_resp
    0x09: button_switch_mode
    0x19: button_switch_mode_resp
    0x0A: rgb_led_control
    0x1A: rgb_led_control_resp
    0x0B: rs485_baud_rate
    0x1B: rs485_baud_rate_resp
    0x0C: device_id
    0x1C: device_id_resp
    0x0D: motor_jam_protection
    0x1D: motor_jam_protection_resp
    0x0E: motor_position_over_range_protection
    0x1E: motor_position_over_range_protection_resp
    # --- Loop Control Instruction Set ---
    0x20: speed_control
    0x30: speed_control_resp
    0x21: speed_pid_config
    0x31: speed_pid_config_resp
    0x22: position_control
    0x32: position_control_resp
    0x23: position_pid_config
    0x33: position_pid_config_resp
    0x24: current_control
    0x34: current_control_resp
    # --- Status Readback Instruction Set ---
    0x40: motor_status_readback
    0x50: motor_status_readback_resp
    0x41: other_status_readback
    0x51: other_status_readback_resp
    0x42: readback_2
    0x52: readback_2_resp
    0x43: readback_3
    0x53: readback_3_resp
    # --- RS485 to I2C Forwarding Control ---
    0x60: i2c_read_register
    0x70: i2c_read_register_resp
    0x61: i2c_write_register
    0x71: i2c_write_register_resp
    0x62: i2c_read_raw
    0x72: i2c_read_raw_resp
    0x63: i2c_write_raw
    0x73: i2c_write_raw_resp
