"""CLI パーサーおよび run() 関数のテスト."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from roller485.cli import create_parser, run
from roller485.util import Roller485Util


# ---------------------------------------------------------------------------
# create_parser() — サブコマンドのパーステスト
# ---------------------------------------------------------------------------


class TestCreateParser:
    """create_parser() が正しい ArgumentParser を返すことを検証."""

    def _parse(self, *args: str):
        parser = create_parser()
        return parser.parse_args(args)

    # --- 基本オプション ---
    def test_port_required(self) -> None:
        """--port が必須."""
        with pytest.raises(SystemExit):
            self._parse("motor-switch", "on")

    def test_default_target(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "motor-switch", "on")
        assert ns.target == 0

    def test_default_baudrate(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "motor-switch", "on")
        assert ns.baudrate == 115200

    def test_default_timeout(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "motor-switch", "on")
        assert ns.timeout == 1.0

    def test_custom_target(self) -> None:
        ns = self._parse(
            "--port", "/dev/ttyUSB0", "--target", "5", "motor-switch", "on"
        )
        assert ns.target == 5

    # --- motor-switch ---
    def test_motor_switch_on(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "motor-switch", "on")
        assert ns.command == "motor-switch"
        assert ns.state == "on"

    def test_motor_switch_off(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "motor-switch", "off")
        assert ns.state == "off"

    def test_motor_switch_invalid(self) -> None:
        with pytest.raises(SystemExit):
            self._parse("--port", "/dev/ttyUSB0", "motor-switch", "invalid")

    # --- mode-setting ---
    @pytest.mark.parametrize("mode", ["speed", "position", "current", "encoder"])
    def test_mode_setting(self, mode: str) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "mode-setting", mode)
        assert ns.command == "mode-setting"
        assert ns.mode == mode

    # --- set-speed-and-max-current ---
    def test_set_speed_and_max_current(self) -> None:
        ns = self._parse(
            "--port",
            "/dev/ttyUSB0",
            "set-speed-and-max-current",
            "100",
            "500.0",
        )
        assert ns.command == "set-speed-and-max-current"
        assert ns.speed == 100
        assert ns.max_current == 500.0

    # --- set-speed-pid ---
    def test_set_speed_pid(self) -> None:
        ns = self._parse(
            "--port",
            "/dev/ttyUSB0",
            "set-speed-pid",
            "1.5",
            "0.1",
            "0.05",
        )
        assert ns.command == "set-speed-pid"
        assert ns.p == 1.5
        assert ns.i == 0.1
        assert ns.d == 0.05

    # --- set-current ---
    def test_set_current(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "set-current", "500.5")
        assert ns.command == "set-current"
        assert ns.current == 500.5

    # --- get-motor-status ---
    def test_get_motor_status(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "get-motor-status")
        assert ns.command == "get-motor-status"

    # --- get-other-status ---
    def test_get_other_status(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "get-other-status")
        assert ns.command == "get-other-status"

    # --- rgb-led-control ---
    def test_rgb_led_control_defaults(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "rgb-led-control")
        assert ns.command == "rgb-led-control"
        assert ns.r == 0
        assert ns.g == 0
        assert ns.b == 0
        assert ns.mode == 0
        assert ns.brightness == 100

    def test_rgb_led_control_custom(self) -> None:
        ns = self._parse(
            "--port",
            "/dev/ttyUSB0",
            "rgb-led-control",
            "--r",
            "255",
            "--g",
            "128",
            "--b",
            "64",
            "--mode",
            "1",
            "--brightness",
            "50",
        )
        assert ns.r == 255
        assert ns.g == 128
        assert ns.b == 64
        assert ns.mode == 1
        assert ns.brightness == 50

    # --- set-rs485-baud-rate ---
    @pytest.mark.parametrize("rate", ["115200", "19200", "9600"])
    def test_set_rs485_baud_rate(self, rate: str) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "set-rs485-baud-rate", rate)
        assert ns.command == "set-rs485-baud-rate"
        assert ns.baud_rate == rate

    # --- set-device-id ---
    def test_set_device_id(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "set-device-id", "5")
        assert ns.command == "set-device-id"
        assert ns.device_id == 5

    # --- save-to-flash ---
    def test_save_to_flash(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "save-to-flash")
        assert ns.command == "save-to-flash"

    # --- set-encoder ---
    def test_set_encoder(self) -> None:
        ns = self._parse("--port", "/dev/ttyUSB0", "set-encoder", "1000")
        assert ns.command == "set-encoder"
        assert ns.value == 1000

    # --- read-i2c ---
    def test_read_i2c(self) -> None:
        ns = self._parse(
            "--port",
            "/dev/ttyUSB0",
            "read-i2c",
            "0x50",
            "1",
            "0x00",
            "4",
        )
        assert ns.command == "read-i2c"
        assert ns.addr == 0x50
        assert ns.reg_len == 1
        assert ns.reg_addr == 0x00
        assert ns.data_len == 4

    # --- write-i2c ---
    def test_write_i2c(self) -> None:
        ns = self._parse(
            "--port",
            "/dev/ttyUSB0",
            "write-i2c",
            "0x50",
            "1",
            "0x00",
            "0102ff",
        )
        assert ns.command == "write-i2c"
        assert ns.data == "0102ff"

    # --- サブコマンドなし ---
    def test_no_subcommand(self) -> None:
        with pytest.raises(SystemExit):
            self._parse("--port", "/dev/ttyUSB0")


# ---------------------------------------------------------------------------
# run() — コマンド実行のテスト
# ---------------------------------------------------------------------------


class TestRun:
    """run() が Roller485Util の正しいメソッドを呼び出すことを検証."""

    def _make_args(self, **kwargs):
        """argparse.Namespace のモックを作成する."""
        defaults = {
            "port": "/dev/ttyUSB0",
            "target": 0,
            "baudrate": 115200,
            "timeout": 1.0,
        }
        defaults.update(kwargs)

        ns = MagicMock()
        for k, v in defaults.items():
            setattr(ns, k, v)
        return ns

    @patch("roller485.cli.Roller485Util")
    def test_motor_switch_on_calls_correct_method(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.motor_switch.return_value = True
        # Enum はリアルクラスの値を使う
        MockClass.Switch = Roller485Util.Switch

        args = self._make_args(command="motor-switch", state="on")
        exit_code = run(args)

        mock_inst.motor_switch.assert_called_once_with(Roller485Util.Switch.On)
        assert exit_code == 0

    @patch("roller485.cli.Roller485Util")
    def test_get_motor_status_returns_json(self, MockClass: MagicMock, capsys) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.get_motor_status.return_value = {
            "speed": 100.0,
            "position": 0.0,
            "current": 50.0,
            "mode": 1,
            "status": 0,
            "error": 0,
        }

        args = self._make_args(command="get-motor-status")
        exit_code = run(args)

        assert exit_code == 0
        captured = capsys.readouterr()
        assert "100.0" in captured.out

    @patch("roller485.cli.Roller485Util")
    def test_set_speed_pid(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.set_speed_pid.return_value = True

        args = self._make_args(command="set-speed-pid", p=1.5, i=0.1, d=0.05)
        exit_code = run(args)

        mock_inst.set_speed_pid.assert_called_once_with(1.5, 0.1, 0.05)
        assert exit_code == 0

    @patch("roller485.cli.Roller485Util")
    def test_failed_command_returns_1(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.motor_switch.return_value = False
        MockClass.Switch = Roller485Util.Switch

        args = self._make_args(command="motor-switch", state="on")
        exit_code = run(args)

        assert exit_code == 1

    @patch("roller485.cli.Roller485Util")
    def test_set_current(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.set_current.return_value = True

        args = self._make_args(command="set-current", current=500.5)
        exit_code = run(args)

        mock_inst.set_current.assert_called_once_with(500.5)
        assert exit_code == 0

    @patch("roller485.cli.Roller485Util")
    def test_save_to_flash(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.save_to_flash.return_value = True

        args = self._make_args(command="save-to-flash")
        exit_code = run(args)

        mock_inst.save_to_flash.assert_called_once()
        assert exit_code == 0

    @patch("roller485.cli.Roller485Util")
    def test_rgb_led_control(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.rgb_led_control.return_value = True

        args = self._make_args(
            command="rgb-led-control",
            r=255,
            g=128,
            b=64,
            mode=1,
            brightness=50,
        )
        exit_code = run(args)

        mock_inst.rgb_led_control.assert_called_once_with(
            r=255, g=128, b=64, mode=1, brightness=50
        )
        assert exit_code == 0

    @patch("roller485.cli.Roller485Util")
    def test_mode_setting_speed(self, MockClass: MagicMock) -> None:
        mock_inst = MockClass.return_value
        mock_inst.is_open = True
        mock_inst.mode_setting.return_value = True
        MockClass.MotorMode = Roller485Util.MotorMode

        args = self._make_args(command="mode-setting", mode="speed")
        exit_code = run(args)

        mock_inst.mode_setting.assert_called_once_with(Roller485Util.MotorMode.Speed)
        assert exit_code == 0
