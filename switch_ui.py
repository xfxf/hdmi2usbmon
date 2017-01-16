#!/usr/bin/python3
"""
Basic UI to swap opsis inputs via hdmi2usb
Requires 'nextgen' hdmi2usb firmware post 15 Jan 2016.
"""
import logging
import socket
import sys
import tkinter
from collections import OrderedDict

from hdmi2usbmon.device import Hdmi2UsbDevice


class Hdmi2UsbException(Exception): pass


class Hdmi2Usb(object):

    MATRIX_INPUTS = OrderedDict([
        ('1', 'input0'),
        ('2', 'input1'),
        ('p', 'pattern'),
    ])

    MATRIX_OUTPUTS = OrderedDict([
        (',', 'output0'),
        ('.', 'output1'),
        ('e', 'encoder'),
    ])

    def __init__(self, host, port):
        self.device = self.get_hdmi2usb(host, port)

    # possible __call__ wrapper to catch socket timeout; reconnect

    def get_hdmi2usb(self, host='localhost', port=8501):
        print("Attempting to connect to hdmi2usbd...")
        h = Hdmi2UsbDevice(host, port)
        h.connect()
        #h.sock.settimeout(5)
        print("Connected.")
        device = h.sock.makefile(mode='rwb')
        return device

    def write(self, data):
       self.device.write(data)
       self.device.flush()

    def connect_input_output(self, input, output):
        if input in self.inputs and output in self.outputs:
            print("Connecting {} to {}...".format(input, output))
            input = input.encode()
            output = output.encode()
            self.write(b'%b on\r\n' % (input))
            self.write(b'video_matrix connect %b %b\r\n' % (input, output))
        else:
            raise Hdmi2UsbException('Invalid input or output')

    def enable_device_info(self):
        self.write(b'debug input0 on\r\n')
        self.write(b'debug input1 on\r\n')
        self.write(b'status short on\r\n')
        self.flush()

    @property
    def inputs(self):
        return self.MATRIX_INPUTS.values()

    @property
    def outputs(self):
        return self.MATRIX_OUTPUTS.values()


class Hdmi2UsbControlUI(object):

    def __init__(self, host, port):
        self.device = Hdmi2Usb(host, port)
        self.root = self.draw_root_window()
        self.selected_input = None
        self.selected_output = None
        self.matrix_buttons = {}
        self.draw_all_widgets()

    def draw_all_widgets(self):
        frame_left = tkinter.Frame(self.root, width=60, height=60)
        frame_left.pack(side=tkinter.LEFT)
        self.gen_matrix_buttons(frame_left, self.device.MATRIX_INPUTS)

        frame_right = tkinter.Frame(self.root, width=60, height=60)
        frame_right.pack(side=tkinter.RIGHT)
        self.gen_matrix_buttons(frame_right, self.device.MATRIX_OUTPUTS)

        frame_bottom = tkinter.Frame(self.root, width=120, height=60)
        frame_bottom.pack(side=tkinter.BOTTOM)
        confirm_button = tkinter.Button(frame_bottom,
                                          text='CONFIRM',
                                          command=self.confirm_matrix_select)
        confirm_button.pack()
        self.root.bind('<Return>', self.confirm_matrix_select())

        bottom_label = tkinter.Label(frame_bottom,
                                     text='Select an input + output, then CONFIRM')
        bottom_label.pack(side=tkinter.BOTTOM)
        self.root.focus_set()


    def draw_root_window(self):
        root = tkinter.Tk()
        #root.geometry('600x250')
        root.wm_title("HDMI2USB Control")
        return root

    def gen_matrix_buttons(self, base, items):
        for key, item in items.items():
            self.matrix_buttons[item] = tkinter.Button(
                base,
                text="{} [{}]".format(item, key),
                command=lambda item=item:self.select_matrix(item)
            )
            self.matrix_buttons[item].pack(side=tkinter.TOP)
            self.root.bind(key, lambda item=item:self.select_matrix(item))
            self.matrix_buttons[item].config(width=20)

    def select_matrix(self, item):
        """Deselects existing input/output, selects input/output, changes state"""
        if item in self.device.inputs:
            if self.selected_input:
                self.matrix_buttons[self.selected_input].config(relief=tkinter.RAISED)
            self.selected_input = item
            self.matrix_buttons[item].config(relief=tkinter.SUNKEN)
        if item in self.device.outputs:
            if self.selected_output:
                self.matrix_buttons[self.selected_output].config(relief=tkinter.RAISED)
            self.selected_output = item
            self.matrix_buttons[item].config(relief=tkinter.SUNKEN)
        self.root.focus_set()

    def confirm_matrix_select(self):
        if self.selected_input and self.selected_output:
            self.device.connect_input_output(self.selected_input,
                                             self.selected_output)
        self.root.focus_set()

"""
while h.connected:
        try:
            line = device.readline()

            if line:
                line = line.strip()
                try:
                    logging.info(line.decode('ascii'))
                except UnicodeDecodeError:
                    # non-ascii byte encountered (i.e. a ^C)
                    logging.info(line)

        except socket.timeout:
            # either not getting data, or connection terminated
            h.close()
"""


if __name__ == "__main__":
    h = Hdmi2UsbControlUI('localhost', 8501)
    h.root.mainloop()


