"""roller485 CLI - Unit-Roller485 制御ツール

使用例:
    python -m roller485 --port /dev/ttyUSB0 motor-switch on
    python -m roller485 --port /dev/ttyUSB0 get-motor-status
"""

import argparse
import json
import sys
import time

from roller485.util import Roller485Util


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="roller485",
        description="Unit-Roller485 CLI 制御ツール",
    )
    parser.add_argument(
        "--port",
        required=True,
        help="シリアルポート (例: /dev/ttyUSB0, /dev/tty.usbserial-10)",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=0,
        help="対象デバイスID (デフォルト: 0)",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="ボーレート (デフォルト: 115200)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="タイムアウト秒 (デフォルト: 1.0)",
    )

    sub = parser.add_subparsers(dest="command", help="実行するコマンド")
    sub.required = True

    # --- motor-switch ---
    p = sub.add_parser("motor-switch", help="モーターON/OFF")
    p.add_argument("state", choices=["on", "off"], help="on または off")

    # --- mode-setting ---
    p = sub.add_parser("mode-setting", help="モード設定 (フラッシュ保存)")
    p.add_argument(
        "mode",
        choices=["speed", "position", "current", "encoder"],
        help="モード: speed(1), position(2), current(3), encoder(4)",
    )

    # --- remove-protection ---
    p = sub.add_parser("remove-protection", help="保護解除")
    p.add_argument("status", type=int, help="保護解除ステータス (0-255)")

    # --- save-to-flash ---
    sub.add_parser("save-to-flash", help="フラッシュメモリに保存")

    # --- set-encoder ---
    p = sub.add_parser("set-encoder", help="エンコーダの設定")
    p.add_argument("value", type=int, help="エンコーダの値")

    # --- button-switching-mode ---
    p = sub.add_parser("button-switching-mode", help="ボタンの切り替えモード設定")
    p.add_argument("mode", choices=["on", "off"], help="on または off")

    # --- rgb-led-control ---
    p = sub.add_parser("rgb-led-control", help="LED制御 (フラッシュ保存)")
    p.add_argument("--r", type=int, default=0, help="赤 (0-255, デフォルト: 0)")
    p.add_argument("--g", type=int, default=0, help="緑 (0-255, デフォルト: 0)")
    p.add_argument("--b", type=int, default=0, help="青 (0-255, デフォルト: 0)")
    p.add_argument(
        "--mode",
        type=int,
        default=0,
        choices=[0, 1],
        help="0: システム表示, 1: ユーザー制御 (デフォルト: 0)",
    )
    p.add_argument(
        "--brightness", type=int, default=100, help="明るさ (0-100, デフォルト: 100)"
    )

    # --- set-rs485-baud-rate ---
    p = sub.add_parser("set-rs485-baud-rate", help="RS485ボーレート設定 (フラッシュ保存)")
    p.add_argument(
        "baud_rate",
        choices=["115200", "19200", "9600"],
        help="ボーレート: 115200, 19200, 9600",
    )

    # --- set-device-id ---
    p = sub.add_parser("set-device-id", help="デバイスID設定 (フラッシュ保存)")
    p.add_argument("device_id", type=int, help="デバイスID (0-255)")

    # --- set-motor-jam-protection ---
    p = sub.add_parser("set-motor-jam-protection", help="モータジャム保護の設定")
    p.add_argument("enable", choices=["on", "off"], help="on: 有効, off: 無効")

    # --- set-motor-position-over-range-protection ---
    p = sub.add_parser(
        "set-motor-position-over-range-protection",
        help="モータ位置オーバーレンジ保護の設定 (フラッシュ保存)",
    )
    p.add_argument("enable", choices=["on", "off"], help="on: 有効, off: 無効")

    # --- set-speed-and-max-current ---
    p = sub.add_parser("set-speed-and-max-current", help="モータ速度と最大電流の設定")
    p.add_argument("speed", type=int, help="速度 (-21000000〜21000000) [RPM]")
    p.add_argument("max_current", type=float, help="最大電流 (-1200〜1200) [mA]")

    # --- set-speed-pid ---
    p = sub.add_parser("set-speed-pid", help="モータ速度PID設定 (フラッシュ保存)")
    p.add_argument("p", type=float, help="P値")
    p.add_argument("i", type=float, help="I値")
    p.add_argument("d", type=float, help="D値")

    # --- set-position-and-max-current ---
    p = sub.add_parser("set-position-and-max-current", help="モータ位置と最大電流の設定")
    p.add_argument("position", type=int, help="位置 (-21000000〜21000000) [counts]")
    p.add_argument("max_current", type=float, help="最大電流 (-1200〜1200) [mA]")

    # --- set-position-pid ---
    p = sub.add_parser("set-position-pid", help="モータ位置PID設定 (フラッシュ保存)")
    p.add_argument("p", type=float, help="P値")
    p.add_argument("i", type=float, help="I値")
    p.add_argument("d", type=float, help="D値")

    # --- set-current ---
    p = sub.add_parser("set-current", help="モータ電流の設定")
    p.add_argument("current", type=float, help="電流 (-1200〜1200) [mA]")

    # --- get-motor-status ---
    sub.add_parser("get-motor-status", help="モータの状態を読み取り")

    # --- get-other-status ---
    sub.add_parser("get-other-status", help="その他の状態を読み取り")

    # --- get-speed-pid-and-rgb ---
    sub.add_parser("get-speed-pid-and-rgb", help="速度PIDとRGBの状態を読み取り")

    # --- get-position-pid-and-other ---
    sub.add_parser("get-position-pid-and-other", help="位置PIDとIDの状態を読み取り")

    # --- read-i2c ---
    p = sub.add_parser("read-i2c", help="I2Cレジスタ読み取り")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2Cアドレス (例: 0x50)")
    p.add_argument(
        "reg_len", type=int, choices=[0, 1], help="レジスタ長 (0: 1byte, 1: 2byte)"
    )
    p.add_argument(
        "reg_addr", type=lambda x: int(x, 0), help="レジスタアドレス (例: 0x00)"
    )
    p.add_argument("data_len", type=int, help="読み取りデータ長 (0-16)")

    # --- write-i2c ---
    p = sub.add_parser("write-i2c", help="I2Cレジスタ書き込み")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2Cアドレス (例: 0x50)")
    p.add_argument(
        "reg_len", type=int, choices=[0, 1], help="レジスタ長 (0: 1byte, 1: 2byte)"
    )
    p.add_argument(
        "reg_addr", type=lambda x: int(x, 0), help="レジスタアドレス (例: 0x00)"
    )
    p.add_argument("data", help="書き込みデータ (hex文字列, 例: 0102ff)")

    # --- read-i2c-raw ---
    p = sub.add_parser("read-i2c-raw", help="I2Cローデータ読み取り")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2Cアドレス (例: 0x50)")
    p.add_argument("data_len", type=int, help="読み取りデータ長 (0-16)")

    # --- write-i2c-raw ---
    p = sub.add_parser("write-i2c-raw", help="I2Cローデータ書き込み")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2Cアドレス (例: 0x50)")
    p.add_argument(
        "stop_bit", type=int, choices=[0, 1], help="ストップビット (0: なし, 1: あり)"
    )
    p.add_argument("data", help="書き込みデータ (hex文字列, 例: 0102ff)")

    return parser


def run(args: argparse.Namespace) -> int:
    """コマンドを実行して終了コードを返す"""
    r485 = Roller485Util(
        target=args.target,
        port=args.port,
        baudrate=args.baudrate,
        timeout=args.timeout,
    )

    try:
        while not r485.is_open:
            time.sleep(0.1)

        cmd = args.command

        # --- 設定系コマンド (bool を返す) ---
        if cmd == "motor-switch":
            state = (
                Roller485Util.Switch.On
                if args.state == "on"
                else Roller485Util.Switch.Off
            )
            ok = r485.motor_switch(state)

        elif cmd == "mode-setting":
            mode_map = {
                "speed": Roller485Util.MotorMode.Speed,
                "position": Roller485Util.MotorMode.Position,
                "current": Roller485Util.MotorMode.Current,
                "encoder": Roller485Util.MotorMode.Encoder,
            }
            ok = r485.mode_setting(mode_map[args.mode])

        elif cmd == "remove-protection":
            ok = r485.remove_protection(args.status)

        elif cmd == "save-to-flash":
            ok = r485.save_to_flash()

        elif cmd == "set-encoder":
            ok = r485.set_encoder(args.value)

        elif cmd == "button-switching-mode":
            mode = (
                Roller485Util.ButtonMode.On
                if args.mode == "on"
                else Roller485Util.ButtonMode.Off
            )
            ok = r485.button_switching_mode(mode)

        elif cmd == "rgb-led-control":
            ok = r485.rgb_led_control(
                r=args.r,
                g=args.g,
                b=args.b,
                mode=args.mode,
                brightness=args.brightness,
            )

        elif cmd == "set-rs485-baud-rate":
            baud_map = {
                "115200": Roller485Util.RS485BaudRate.Baud115200,
                "19200": Roller485Util.RS485BaudRate.Baud19200,
                "9600": Roller485Util.RS485BaudRate.Baud9600,
            }
            ok = r485.set_rs485_baud_rate(baud_map[args.baud_rate])

        elif cmd == "set-device-id":
            ok = r485.set_device_id(args.device_id)

        elif cmd == "set-motor-jam-protection":
            ok = r485.set_motor_jam_protection(args.enable == "on")

        elif cmd == "set-motor-position-over-range-protection":
            ok = r485.set_motor_position_over_range_protection(args.enable == "on")

        elif cmd == "set-speed-and-max-current":
            ok = r485.set_speed_and_max_current(args.speed, args.max_current)

        elif cmd == "set-speed-pid":
            ok = r485.set_speed_pid(args.p, args.i, args.d)

        elif cmd == "set-position-and-max-current":
            ok = r485.set_position_and_max_current(args.position, args.max_current)

        elif cmd == "set-position-pid":
            ok = r485.set_position_pid(args.p, args.i, args.d)

        elif cmd == "set-current":
            ok = r485.set_current(args.current)

        # --- 読み取り系コマンド (dict を返す) ---
        elif cmd == "get-motor-status":
            result = r485.get_motor_status()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result else 1

        elif cmd == "get-other-status":
            result = r485.get_other_status()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result else 1

        elif cmd == "get-speed-pid-and-rgb":
            result = r485.get_speed_pid_and_rgb()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result else 1

        elif cmd == "get-position-pid-and-other":
            result = r485.get_position_pid_and_other()
            print(json.dumps(result, indent=2, ensure_ascii=False))
            return 0 if result else 1

        # --- I2C系コマンド ---
        elif cmd == "read-i2c":
            data = r485.read_i2c(args.addr, args.reg_len, args.reg_addr, args.data_len)
            if data:
                print(data.hex())
                return 0
            else:
                print("読み取り失敗", file=sys.stderr)
                return 1

        elif cmd == "write-i2c":
            data = bytes.fromhex(args.data)
            ok = r485.write_i2c(args.addr, args.reg_len, args.reg_addr, data)

        elif cmd == "read-i2c-raw":
            data = r485.read_i2c_raw(args.addr, args.data_len)
            if data:
                print(data.hex())
                return 0
            else:
                print("読み取り失敗", file=sys.stderr)
                return 1

        elif cmd == "write-i2c-raw":
            data = bytes.fromhex(args.data)
            ok = r485.write_i2c_raw(args.addr, args.stop_bit, data)

        else:
            print(f"不明なコマンド: {cmd}", file=sys.stderr)
            return 1

        # 設定系・書き込み系の結果表示
        if ok:
            print("OK")
            return 0
        else:
            print("FAILED", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"エラー: {e}", file=sys.stderr)
        return 1

    finally:
        r485.flush()
        r485.close()


def main():
    parser = create_parser()
    args = parser.parse_args()
    sys.exit(run(args))


if __name__ == "__main__":
    main()
