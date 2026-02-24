"""roller485 CLI - Unit-Roller485 control tool

Examples:
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
        description="Unit-Roller485 CLI control tool",
    )
    parser.add_argument(
        "--port",
        required=True,
        help="Serial port (e.g. /dev/ttyUSB0, /dev/tty.usbserial-10)",
    )
    parser.add_argument(
        "--target",
        type=int,
        default=0,
        help="Target device ID (default: 0)",
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=115200,
        help="Baud rate (default: 115200)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=1.0,
        help="Timeout in seconds (default: 1.0)",
    )

    sub = parser.add_subparsers(dest="command", help="Command to execute")
    sub.required = True

    # --- motor-switch ---
    p = sub.add_parser("motor-switch", help="Turn motor ON/OFF")
    p.add_argument("state", choices=["on", "off"], help="on or off")

    # --- mode-setting ---
    p = sub.add_parser("mode-setting", help="Set motor mode (saved to flash)")
    p.add_argument(
        "mode",
        choices=["speed", "position", "current", "encoder"],
        help="Mode: speed(1), position(2), current(3), encoder(4)",
    )

    # --- remove-protection ---
    p = sub.add_parser("remove-protection", help="Remove protection")
    p.add_argument("status", type=int, help="Protection removal status (0-255)")

    # --- save-to-flash ---
    sub.add_parser("save-to-flash", help="Save settings to flash memory")

    # --- set-encoder ---
    p = sub.add_parser("set-encoder", help="Set encoder value")
    p.add_argument("value", type=int, help="Encoder value")

    # --- button-switching-mode ---
    p = sub.add_parser("button-switching-mode", help="Set button switching mode")
    p.add_argument("mode", choices=["on", "off"], help="on or off")

    # --- rgb-led-control ---
    p = sub.add_parser("rgb-led-control", help="Control RGB LED (saved to flash)")
    p.add_argument("--r", type=int, default=0, help="Red (0-255, default: 0)")
    p.add_argument("--g", type=int, default=0, help="Green (0-255, default: 0)")
    p.add_argument("--b", type=int, default=0, help="Blue (0-255, default: 0)")
    p.add_argument(
        "--mode",
        type=int,
        default=0,
        choices=[0, 1],
        help="0: System display, 1: User control (default: 0)",
    )
    p.add_argument(
        "--brightness", type=int, default=100, help="Brightness (0-100, default: 100)"
    )

    # --- set-rs485-baud-rate ---
    p = sub.add_parser(
        "set-rs485-baud-rate", help="Set RS485 baud rate (saved to flash)"
    )
    p.add_argument(
        "baud_rate",
        choices=["115200", "19200", "9600"],
        help="Baud rate: 115200, 19200, 9600",
    )

    # --- set-device-id ---
    p = sub.add_parser("set-device-id", help="Set device ID (saved to flash)")
    p.add_argument("device_id", type=int, help="Device ID (0-255)")

    # --- set-motor-jam-protection ---
    p = sub.add_parser("set-motor-jam-protection", help="Set motor jam protection")
    p.add_argument("enable", choices=["on", "off"], help="on: enable, off: disable")

    # --- set-motor-position-over-range-protection ---
    p = sub.add_parser(
        "set-motor-position-over-range-protection",
        help="Set motor position over-range protection (saved to flash)",
    )
    p.add_argument("enable", choices=["on", "off"], help="on: enable, off: disable")

    # --- set-speed-and-max-current ---
    p = sub.add_parser(
        "set-speed-and-max-current", help="Set motor speed and max current"
    )
    p.add_argument("speed", type=int, help="Speed (-21000000 to 21000000) [RPM]")
    p.add_argument("max_current", type=float, help="Max current (-1200 to 1200) [mA]")

    # --- set-speed-pid ---
    p = sub.add_parser(
        "set-speed-pid", help="Set speed PID parameters (saved to flash)"
    )
    p.add_argument("p", type=float, help="P value")
    p.add_argument("i", type=float, help="I value")
    p.add_argument("d", type=float, help="D value")

    # --- set-position-and-max-current ---
    p = sub.add_parser(
        "set-position-and-max-current", help="Set motor position and max current"
    )
    p.add_argument(
        "position", type=int, help="Position (-21000000 to 21000000) [counts]"
    )
    p.add_argument("max_current", type=float, help="Max current (-1200 to 1200) [mA]")

    # --- set-position-pid ---
    p = sub.add_parser(
        "set-position-pid", help="Set position PID parameters (saved to flash)"
    )
    p.add_argument("p", type=float, help="P value")
    p.add_argument("i", type=float, help="I value")
    p.add_argument("d", type=float, help="D value")

    # --- set-current ---
    p = sub.add_parser("set-current", help="Set motor current")
    p.add_argument("current", type=float, help="Current (-1200 to 1200) [mA]")

    # --- get-motor-status ---
    sub.add_parser("get-motor-status", help="Read motor status")

    # --- get-other-status ---
    sub.add_parser("get-other-status", help="Read other status")

    # --- get-speed-pid-and-rgb ---
    sub.add_parser("get-speed-pid-and-rgb", help="Read speed PID and RGB status")

    # --- get-position-pid-and-other ---
    sub.add_parser(
        "get-position-pid-and-other", help="Read position PID and other status"
    )

    # --- read-i2c ---
    p = sub.add_parser("read-i2c", help="Read I2C register")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2C address (e.g. 0x50)")
    p.add_argument(
        "reg_len", type=int, choices=[0, 1], help="Register length (0: 1byte, 1: 2byte)"
    )
    p.add_argument(
        "reg_addr", type=lambda x: int(x, 0), help="Register address (e.g. 0x00)"
    )
    p.add_argument("data_len", type=int, help="Data length to read (0-16)")

    # --- write-i2c ---
    p = sub.add_parser("write-i2c", help="Write I2C register")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2C address (e.g. 0x50)")
    p.add_argument(
        "reg_len", type=int, choices=[0, 1], help="Register length (0: 1byte, 1: 2byte)"
    )
    p.add_argument(
        "reg_addr", type=lambda x: int(x, 0), help="Register address (e.g. 0x00)"
    )
    p.add_argument("data", help="Data to write (hex string, e.g. 0102ff)")

    # --- read-i2c-raw ---
    p = sub.add_parser("read-i2c-raw", help="Read raw I2C data")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2C address (e.g. 0x50)")
    p.add_argument("data_len", type=int, help="Data length to read (0-16)")

    # --- write-i2c-raw ---
    p = sub.add_parser("write-i2c-raw", help="Write raw I2C data")
    p.add_argument("addr", type=lambda x: int(x, 0), help="I2C address (e.g. 0x50)")
    p.add_argument(
        "stop_bit", type=int, choices=[0, 1], help="Stop bit (0: none, 1: present)"
    )
    p.add_argument("data", help="Data to write (hex string, e.g. 0102ff)")

    return parser


def run(args: argparse.Namespace) -> int:
    """Execute a command and return the exit code."""
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

        # --- Setting commands (return bool) ---
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

        # --- Read commands (return dict) ---
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

        # --- I2C commands ---
        elif cmd == "read-i2c":
            data = r485.read_i2c(args.addr, args.reg_len, args.reg_addr, args.data_len)
            if data:
                print(data.hex())
                return 0
            else:
                print("Read failed", file=sys.stderr)
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
                print("Read failed", file=sys.stderr)
                return 1

        elif cmd == "write-i2c-raw":
            data = bytes.fromhex(args.data)
            ok = r485.write_i2c_raw(args.addr, args.stop_bit, data)

        else:
            print(f"Unknown command: {cmd}", file=sys.stderr)
            return 1

        # Display result for setting/write commands
        if ok:
            print("OK")
            return 0
        else:
            print("FAILED", file=sys.stderr)
            return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
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
