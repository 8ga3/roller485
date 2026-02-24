# roller485

M5Stack Unit-Roller485 を Python から制御するためのモジュールです。RS485 シリアル通信を介してモーター制御、ステータス読み出し、I2C 転送などの操作を行えます。

## 必要条件

- Python >= 3.9
- [kaitaistruct](https://pypi.org/project/kaitaistruct/) >= 0.11
- [pyserial](https://pypi.org/project/pyserial/) >= 3.5

## インストール

```sh
pip install .
```

または開発モード:

```sh
pip install -e .
```

## 使い方

### CLI

`roller485` コマンドでターミナルから直接操作できます。

```sh
# モーターステータスの取得
roller485 --port /dev/ttyUSB0 get-motor-status

# モーターON
roller485 --port /dev/ttyUSB0 motor-switch on

# 速度と最大電流の設定
roller485 --port /dev/ttyUSB0 set-speed-and-max-current 100 500

# モーターOFF
roller485 --port /dev/ttyUSB0 motor-switch off
```

#### 共通オプション

| オプション | デフォルト | 説明 |
|---|---|---|
| `--port` | (必須) | シリアルポート (例: `/dev/ttyUSB0`, `/dev/tty.usbserial-10`) |
| `--target` | `0` | デバイスID |
| `--baudrate` | `115200` | ボーレート |
| `--timeout` | `1.0` | タイムアウト (秒) |

#### コマンド一覧

**設定コマンド:**

| コマンド | 説明 |
|---|---|
| `motor-switch <on\|off>` | モーターの ON/OFF |
| `mode-setting <speed\|position\|current\|encoder>` | モーターモード設定 (フラッシュ保存) |
| `remove-protection <status>` | 保護解除 |
| `save-to-flash` | フラッシュメモリに保存 |
| `set-encoder <value>` | エンコーダの設定 |
| `button-switching-mode <on\|off>` | ボタン切替モード設定 |
| `rgb-led-control [--r R] [--g G] [--b B] [--mode MODE] [--brightness BRI]` | RGB LED 制御 (フラッシュ保存) |
| `set-rs485-baud-rate <115200\|19200\|9600>` | RS485 ボーレート設定 (フラッシュ保存) |
| `set-device-id <id>` | デバイスID 設定 (フラッシュ保存) |
| `set-motor-jam-protection <on\|off>` | モータジャム保護設定 |
| `set-motor-position-over-range-protection <on\|off>` | 位置オーバーレンジ保護設定 (フラッシュ保存) |

**制御コマンド:**

| コマンド | 説明 |
|---|---|
| `set-speed-and-max-current <speed> <max_current>` | 速度と最大電流の設定 |
| `set-speed-pid <p> <i> <d>` | 速度 PID 設定 (フラッシュ保存) |
| `set-position-and-max-current <position> <max_current>` | 位置と最大電流の設定 |
| `set-position-pid <p> <i> <d>` | 位置 PID 設定 (フラッシュ保存) |
| `set-current <current>` | 電流の設定 |

**ステータス読み出しコマンド:**

| コマンド | 説明 |
|---|---|
| `get-motor-status` | モーターステータスの取得 |
| `get-other-status` | その他ステータスの取得 |
| `get-speed-pid-and-rgb` | 速度 PID と RGB の取得 |
| `get-position-pid-and-other` | 位置 PID とその他の取得 |

**I2C 転送コマンド:**

| コマンド | 説明 |
|---|---|
| `read-i2c <addr> <reg_len> <reg_addr> <data_len>` | I2C レジスタ読み取り |
| `write-i2c <addr> <reg_len> <reg_addr> <data_hex>` | I2C レジスタ書き込み |
| `read-i2c-raw <addr> <data_len>` | I2C ローデータ読み取り |
| `write-i2c-raw <addr> <stop_bit> <data_hex>` | I2C ローデータ書き込み |

### Python API

```python
import time
from roller485 import Roller485Util

r485 = Roller485Util(
    target=0,
    port="/dev/ttyUSB0",
    baudrate=115200,
    timeout=1,
)

while not r485.is_open:
    time.sleep(0.1)

# モーターステータスの取得
status = r485.get_motor_status()
print(status)

# モーターON
r485.motor_switch(Roller485Util.Switch.On)

# 速度と最大電流の設定 (100 RPM, 500 mA)
# RPMは+が時計回り(CW) -が反時計回り(CCW)
r485.set_speed_and_max_current(100, 500)
time.sleep(5)

# 反時計回り(CCW)
r485.set_speed_and_max_current(-100, 500)
time.sleep(5)

# 速度0にすることで、次回モーター始動したときに
# 急に動き出さないようになる
r485.set_speed_and_max_current(0, 500)
time.sleep(5)

# モーターOFF
r485.motor_switch(Roller485Util.Switch.Off)

r485.flush()
r485.close()
```

## プロトコル定義の再生成

通信プロトコルは [Kaitai Struct](https://kaitai.io/) で定義されています。`roller485.ksy` を編集した場合は以下のコマンドで Python コードを再生成してください。

```sh
kaitai-struct-compiler -t python -w roller485.ksy
```

## ライセンス

MIT License
