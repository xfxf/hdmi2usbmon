#!/usr/bin/python3
"""
Basic script to log hdmi2usbd streaming debug/status messages into a rotating log file.
Requires 'nextgen' hdmi2usb firmware post 15 Jan 2016.
"""
import logging
import socket
import sys

from logging.handlers import TimedRotatingFileHandler
from hdmi2usbmon.device import Hdmi2UsbDevice


def log_setup(log_filename):
    """
    Sets up logging for hourly rotating files in specified location, and stdout
    """
    format = logging.Formatter(
        '%(asctime)s hdmi2usbd [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    logfile_handler = TimedRotatingFileHandler(log_filename,
                                           when="h",
                                           interval=1)
    logfile_handler.setFormatter(format)
    logger.addHandler(logfile_handler)

    stdout_handler = logging.StreamHandler(sys.stdout)
    stdout_handler.setFormatter(format)
    logger.addHandler(stdout_handler)


if __name__ == "__main__":
    log_setup('/var/log/hdmi2usb/hdmi2usb')

    print("Attempting to connect to hdmi2usbd...")
    h = Hdmi2UsbDevice('localhost', 8501)
    h.connect()
    h.sock.settimeout(5)
    print("Connected.")

    device = h.sock.makefile(mode='rwb')

    device.write(b'\r\n')
    device.write(b'version\r\n')
    device.write(b'debug input0 on\r\n')
    device.write(b'debug input1 on\r\n')
    device.write(b'status short on\r\n')
    device.flush()

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

