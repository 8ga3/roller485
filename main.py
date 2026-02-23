import time
import traceback

from util import Roller485Util


def main():
    print("Hello from demo-roller485!")

    PORT = "/dev/tty.usbserial-10"
    TARGET = 0
    BAUDRATE = 115200
    TIMEOUT = 1

    try:
        r485 = Roller485Util(
            target=TARGET, port=PORT, baudrate=BAUDRATE, timeout=TIMEOUT
        )

        while not r485.is_open:
            time.sleep(0.1)  # ビジーループを防ぐため

        print(f"Connection established: {PORT}")

        # モーター始動
        print("Motor ON")
        if not r485.motor_switch(Roller485Util.Switch.On):
            raise Exception("Failed to turn on the motor")

        # 目標モータ速度を設定
        print("Motor CW")
        if not r485.set_speed_and_max_current(100, 500):
            raise Exception("Failed to set speed and max current")
        time.sleep(5)

        print("Motor CCW")
        if not r485.set_speed_and_max_current(-100, 500):
            raise Exception("Failed to set speed and max current")
        time.sleep(5)

        # モーター停止
        print("Motor OFF")
        if not r485.motor_switch(Roller485Util.Switch.Off):
            raise Exception("Failed to turn off the motor")

    except Exception as e:
        print(str(e))
        traceback.print_exc()

    finally:
        r485.flush()
        r485.close()


if __name__ == "__main__":
    main()
