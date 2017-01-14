"""
Basic script to log hdmi2usbd streaming debug/status messages into a rotating log file.
Requires 'nextgen' hdmi2usb firmware post 15 Jan 2016.

Super early hacky version.  Currently does not handle socket disconnects.
"""
import sys
import logging
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
    print("Connected.")

    device = h.sock.makefile(mode='rwb')

    device.write(b'debug input0 off\r\n')
    device.write(b'debug input1 off\r\n')
    device.write(b'status short off\r\n')
    device.flush()

    while h.connected:
        try:
            line = device.readline()
        except OSError:
            line = None

        if line:
            line = line.strip()
            try:
                logging.info(line.decode('ascii'))
            except UnicodeDecodeError:
                # non-ascii byte encountered (i.e. a ^C)
                logging.info(line)
        else:
            pass

