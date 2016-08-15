"""
USB Hdmi2Usb status objects
"""


class ChannelStatus(object):

    def __init__(self, channel):
        self.channel = channel


class Hdmi2UsbStatus(object):

    def __init__(self, port):
        self.connected = False
        self.port = port
        self.devices = [ChannelStatus(0), ChannelStatus(1)]

