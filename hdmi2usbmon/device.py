"""

"""
import os
import socket


def which(program):
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ['PATH'].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None


class Hdmi2UsbDevice(object):
    """
    Representation of a HDMI2USB Device

    """
    LOCALHOST = ['localhost', '127.0.0.1', '::1']

    def __init__(self, host, port, hdmi2usbd=None):
        self.host = host
        self.port = port
        self.prog = hdmi2usbd or 'hdmi2usbd'
        self.sock = None  # type: socket.socket

    @property
    def connected(self):
        return self.sock is not None

    def remoteaddr(self, host=None, port=None):
        if host is not None:
            self.host = host
        if port is not None:
            self.port = port
        return self.host, self.port

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None

    def connect(self, host=None, port=None):
        address = self.remoteaddr(host, port)
        if not self.connected:
            self.sock = socket.create_connection(address)
            self.sock.setblocking(0)
        return self.connected

    def start_daemon(self, program=None):
        if program is not None:
            self.prog = program
        args = list()
        if self.host:
            args.extend(['--host', self.host])
        if self.port:
            args.extend(['--port', str(self.port)])
        program = which(self.prog)
        if program is None:
            raise EnvironmentError("can't locate command '{}'".format(self.prog))
        args.insert(0, program)
        import subprocess
        rc = subprocess.call(args)
        return rc
