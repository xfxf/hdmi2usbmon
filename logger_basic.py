"""
Basic script to log hdmi2usbd streaming debug/status messages into a rotating log file.
Requires 'nextgen' hdmi2usb firmware post 15 Jan 2016.

Super early hacky version.  Currently does not handle socket disconnects.
"""

import logging
from logging.handlers import TimedRotatingFileHandler
from hdmi2usbmon.device import Hdmi2UsbDevice


def log_setup(log_filename):
    log_handler = TimedRotatingFileHandler(log_filename,
                                           when="h",
                                           interval=1)
    formatter = logging.Formatter(
        '%(asctime)s hdmi2usbd [%(process)d]: %(message)s',
        '%b %d %H:%M:%S')
    log_handler.setFormatter(formatter)
    logger = logging.getLogger()
    logger.addHandler(log_handler)
    logger.setLevel(logging.INFO)


if __name__ == "__main__":
    log_setup('/var/log/hdmi2usb/hdmi2usb')

    print("Attempting to connect to hdmi2usbd...")
    h = Hdmi2UsbDevice('localhost', 8501)
    h.connect()
    print("Connected.")

    h.sock.send(b'debug input0 on\r\n')
    h.sock.send(b'debug input1 on\r\n')
    h.sock.send(b'status short on\r\n')

    while True:

        buffer = b''

        # get data until no more available
        try:
            while True:
                buffer += h.sock.recv(512)
        except BlockingIOError:
            pass

        # log each line into a file
        if buffer:
            lines = buffer.split(b'\r\n')
            for line in lines:
                if line:
                    print(line)
                    try:
                        logging.info(line.decode('ascii'))
                    except UnicodeDecodeError:
                        # non-ascii byte encountered (i.e. a ^C)
                        logging.info(line)


