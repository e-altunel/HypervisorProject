#
# Copyright 2019 Games Creators Club
#
# MIT License
#
from inputs import get_gamepad, UnpluggedError
import threading
import time


class FakeJoystick:
    """
    A fake joystick implementation for testing: it just returns continuous axis movements and button presses.
    """

    def __init__(self):
        self.count = 0
        self.direction = 1
        self.buttons = {
            "BTN_SOUTH": 0,
            "BTN_EAST": 0,
            "BTN_NORTH": 0,
            "BTN_WEST": 0,
            "BTN_START": 0,
            "BTN_SELECT": 0,
            "BTN_MODE": 0,
            "BTN_THUMBR": 0,
            "BTN_THUMBL": 0,
            "BTN_TR": 0,
            "BTN_TL": 0,
        }
        self.sticks = {"x": 0, "y": 0, "rx": 0, "ry": 0}
        self.running = True
        self.thread = threading.Thread(target=self.run)
        self.thread.start()

    def getEvents(self):
        try:
            events = get_gamepad()
            for event in events:
                self.processEvent(event)
        except OSError:
            return
        except UnpluggedError:
            time.sleep(1)
            return

    def processEvent(self, event):
        if event.ev_type == "Key":
            self.buttons[event.code] = event.state
        elif event.ev_type == "Absolute":
            new_state = event.state // 256
            if new_state < 0:
                new_state += 256
            if event.code == "ABS_X":
                self.sticks["x"] = new_state
            elif event.code == "ABS_Y":
                self.sticks["y"] = new_state
            elif event.code == "ABS_RX":
                self.sticks["rx"] = new_state
            elif event.code == "ABS_RY":
                self.sticks["ry"] = new_state

    def run(self):
        while self.running:
            self.getEvents()
            time.sleep(0.001)

    def stop(self):
        self.running = False
        self.thread.join()

    def readAxis(self):
        return self.sticks

    def readButtons(self):
        return self.buttons


if __name__ == "__main__":

    import sys
    import os

    sys.path.append(os.path.split(os.path.dirname(os.path.realpath(__file__)))[0])

    import bt_joystick

    bluetooth_joystick = bt_joystick.BluetoothJoystickDeviceMain(FakeJoystick())
    bluetooth_joystick.run()
