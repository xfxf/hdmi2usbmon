#!/usr/bin/python3
"""
Simple UI to select opsis inputs via hdmi2usb.
Requires 'nextgen' hdmi2usb firmware post 15 Jan 2016.
"""
import logging
import socket
import sys
import tkinter
import threading
from collections import OrderedDict
from copy import deepcopy
from hdmi2usbmon.device import Hdmi2UsbDevice


class Hdmi2UsbException(Exception): pass


class Hdmi2Usb(object):
    """
    This should eventually turn into the parent Hdmi2UsbDevice once
    sanity prevails and it is functionally complete.  Currently experimental.
    """

    MATRIX_INPUTS = OrderedDict([
        ('input0', 'HDMI IN 1'),
        ('input1', 'HDMI IN 2'),
        ('pattern', 'Pattern'),
    ])

    MATRIX_OUTPUTS = OrderedDict([
        ('output0', 'HDMI OUT 1'),
        ('output1', 'HDMI OUT 2'),
        ('encoder', 'USB Capture'),
    ])

    def __init__(self, host, port):
        # parent_device should be device; workaround as using incomplete library
        self.device, self.parent_device = self.get_hdmi2usb(host, port)

    # possible __call__ wrapper to catch socket timeout; reconnect

    def get_hdmi2usb(self, host='localhost', port=8501):
        h = Hdmi2UsbDevice(host, port)
        h.connect()
        h.sock.settimeout(30)
        print("Connected.")
        device = h.sock.makefile(mode='rwb')
        return device, h

    @property
    def connected(self):
        return self.parent_device.connected

    def write(self, data):
       self.device.write(data)
       self.device.flush()

    def readline(self):
        try:
            return self.device.readline()
        except socket.timeout:
            # doesn't work
            print("Connect timed out, attempting to reconnect...")
            self.device.close()
            self.device.connect()

    def connect_input_output(self, input, output):
        if input in self.inputs and output in self.outputs:
            print("Connecting {} to {}...".format(input, output))
            input = input.encode()
            output = output.encode()
            self.write(b'%b on\r\n' % input)
            self.write(b'video_matrix connect %b %b\r\n' % (input, output))
        else:
            raise Hdmi2UsbException('Invalid input or output')

    def output_off(self, output):
        if output in self.outputs:
            print("Turning output {} off...".format(output))
            output = output.encode()
            self.write(b'%b off\r\n' % output)

    def enable_device_info(self):
        self.write(b'debug input0 on\r\n')
        self.write(b'debug input1 on\r\n')
        self.write(b'status short on\r\n')
        self.flush()

    @property
    def inputs(self):
        return self.MATRIX_INPUTS.keys()

    @property
    def outputs(self):
        return self.MATRIX_OUTPUTS.keys()


class Hdmi2UsbControlUI(object):

    def __init__(self, host, port):
        self.device = Hdmi2Usb(host, port)
        self.root = self.draw_root_window()
        self.debug = None
        self.readthread = self.run_read_thread()
        self.draw_all_widgets()

    def draw_all_widgets(self):
        frames = {}

        for output, name in self.device.MATRIX_OUTPUTS.items():
            frames[output] = tkinter.LabelFrame(self.root, text=name, width=60, height=60)
            frames[output].pack(side=tkinter.TOP)
            Hdmi2UsbControlUIOutputElement(self.device, frames[output], output)

        debug_frame, self.debug = self.draw_debug_window(self.root)
        debug_frame.pack(side=tkinter.TOP)

    def run_read_thread(self):
        thread = threading.Thread(target=self.read_from_device)
        thread.start()
        return thread

    def read_from_device(self):
        while self.device.connected:
            line = self.device.readline()
            if line:
                self.debug.insert(tkinter.END, line)
                self.debug.see(tkinter.END)

    def draw_debug_window(self, root):
        debug_frame = tkinter.LabelFrame(root, text='HDMI2USB Debug')
        debug = tkinter.Text(debug_frame, width=120, height=20)
        debug.pack(side=tkinter.TOP)
        return debug_frame, debug

        """
        confirm_button = tkinter.Button(frame_bottom,
                                          text='CONFIRM',
                                          command=self.confirm_matrix_select)
        confirm_button.pack()
        self.root.bind('<Return>', self.confirm_matrix_select())

        bottom_label = tkinter.Label(frame_bottom,
                                     text='Select an input + output, then CONFIRM')
        bottom_label.pack(side=tkinter.BOTTOM)
        """
        self.root.focus_set()

    def draw_root_window(self):
        root = tkinter.Tk()
        #root.geometry('600x250')
        root.wm_title("HDMI2USB Control")
        return root

"""
"""

class Hdmi2UsbControlUIOutputElement(object):

    def __init__(self, device, root, output):
        self.device = device
        self.root = root
        self.selected_input = None
        self.output = output
        self.matrix_buttons = {}
        self.draw_all_widgets()

    def draw_all_widgets(self):
        output_buttons = deepcopy(self.device.MATRIX_INPUTS)
        output_buttons['off'] = 'OFF'
        self.gen_output_buttons(self.root, output_buttons)

    def gen_output_buttons(self, base, items):
        for item, name in items.items():
            print(item, name)
            self.matrix_buttons[item] = tkinter.Button(
                base,
                text=name,
                command=lambda item=item:self.confirm_matrix_select(item)
            )
            self.matrix_buttons[item].pack(side=tkinter.LEFT)
            self.matrix_buttons[item].config(width=20)

    def confirm_matrix_select(self, input):
        if input is not self.selected_input and input in self.device.inputs:
            if self.selected_input:
                self.matrix_buttons[self.selected_input].config(relief=tkinter.RAISED)
            self.selected_input = input
            self.matrix_buttons[input].config(relief=tkinter.SUNKEN)
            self.device.connect_input_output(input, self.output)
        elif input == 'off':
            if self.selected_input:
                self.matrix_buttons[self.selected_input].config(relief=tkinter.RAISED)
                self.selected_input = None
                self.device.output_off(self.output)
            self.matrix_buttons[input].config(relief=tkinter.SUNKEN)


if __name__ == "__main__":
    h = Hdmi2UsbControlUI('localhost', 8501)
    h.root.mainloop()

