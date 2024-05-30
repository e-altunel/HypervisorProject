#!/usr/bin/env python3

#
# Copyright 2019 Games Creators Club
#
# MIT License
#


import time

from dbus.mainloop.glib import DBusGMainLoop
from bt_joystick import BTDevice
from . import hid_report_descriptor

# if not os.geteuid() == 0:
#     sys.exit("Only root can run this script")


class Joystick:

    def __init__(self):
        pass

    def readAxis(self):
        raise NotImplementedError()

    def readButtons(self):
        raise NotImplementedError()

    # TODO Add way for Joystick implementation to pass 'description' to Main class
    # so it can create appropriate SDP record and handle results


class BluetoothJoystickDeviceMain:
    def __init__(self, joystick):
        self.joystick = joystick

    def run(self):
        DBusGMainLoop(set_as_default=True)

        bt = BTDevice(
            hid_descriptor=hid_report_descriptor.create_joystick_report_descriptor(kind=hid_report_descriptor.Usage.Gamepad, axes=(
                hid_report_descriptor.Usage.X, hid_report_descriptor.Usage.Y, hid_report_descriptor.Usage.Rx, hid_report_descriptor.Usage.Ry,
                ), button_number=16))

        while True:
            re_start = False

            print("Waiting for connections")
            bt.listen()

            button_bits_1 = 0
            button_bits_2 = 0

            axis = [0, 0, 0, 0, ]
            new_axis = [0, 0, 0, 0, ]
            
            has_changes = False

            upload_penalty = 0

            while not re_start:
                joystick_axis = self.joystick.readAxis()
                joystick_buttons = self.joystick.readButtons()

                new_axis[0] = joystick_axis['x']
                new_axis[1] = joystick_axis['y']
                new_axis[2] = joystick_axis['rx']
                new_axis[3] = joystick_axis['ry']

                new_button_bits_1 = 0
                new_button_bits_2 = 0

                # TODO this should really use Joystick description to determine which buttons are sent as which
                # 'trigger', 'tl', 'tr', 'thumb', 'dpad_up', 'dpad_down', 'dpad_left', 'dpad_right', 'thumbl', 'thumbr'
                if joystick_buttons['BTN_NORTH']:
                    new_button_bits_1 |= 1
                if joystick_buttons['BTN_SOUTH']:
                    new_button_bits_1 |= 2
                if joystick_buttons['BTN_WEST']:
                    new_button_bits_1 |= 4
                if joystick_buttons['BTN_EAST']:
                    new_button_bits_1 |= 8

                if joystick_buttons['BTN_START']:
                    new_button_bits_1 |= 16
                if joystick_buttons['BTN_SELECT']:
                    new_button_bits_1 |= 32
                if joystick_buttons['BTN_TR']:
                    new_button_bits_1 |= 64
                if joystick_buttons['BTN_TL']:
                    new_button_bits_1 |= 128

                if joystick_buttons['BTN_THUMBL']:
                    new_button_bits_2 |= 1
                if joystick_buttons['BTN_THUMBR']:
                    new_button_bits_2 |= 2
                if joystick_buttons['BTN_MODE']:
                    new_button_bits_2 |= 4


                for i in range(0, 4):
                    if axis[i] != new_axis[i]:
                        axis[i] = new_axis[i]
                        has_changes = True

                if button_bits_1 != new_button_bits_1 or button_bits_2 != new_button_bits_2:
                    button_bits_1 = new_button_bits_1
                    button_bits_2 = new_button_bits_2
                    has_changes = True

                if has_changes and time.time() >= upload_penalty:
                    upload_penalty = time.time() + 0.01
                    has_changes = False

                    data = bytes((0xA1, 0x01, button_bits_1, button_bits_2, *axis))
                    # print("Changing data " + str(["{:02x}".format(d) for d in data]))
                    try:
                        bt.send_message(data)
                    except Exception as e:
                        print("Failed to send data - disconnected " + str(e))
                        re_start = True

                
                time.sleep(0.001)
                """
                try:
                    bytes_arr = bt.recv_message(1024)
                    if len(bytes_arr) == len(received_vals):
                        for i in range(0, len(received_vals)):
                            received_vals[i] = bytes_arr[i]
                    print("Received data " + str(bytes_arr))
                except BlockingIOError:
                    pass
                except Exception as e:
                    pass
                """
