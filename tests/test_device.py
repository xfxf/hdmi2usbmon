from unittest import TestCase
from hdmi2usbmon.device import Hdmi2UsbDevice, which

class TestDevice(TestCase):

    def setUp(self):
        self.device = Hdmi2UsbDevice('localhost', 8150)

    PROGS = ['ls', 'cat', 'python', 'RuBb1sH']

    def test_which(self):
        """ note: this needs a unix of some sort """
        for i, prog in enumerate(self.PROGS):
            program = which(prog)
            if i == 3:
                self.assertIsNone(program)
            else:
                self.assertIsNotNone(program)

    def try_connect(self):
        self.error = None
        try:
            self.device.connect()
            return True
        except ConnectionRefusedError:
            # we don't appear to be running hdmi2usbd or it isn't listening to our port
            return False
        except Exception as exc:
            self.error = exc
            return False

    def test_connect(self):
        done = False
        while not done:
            self.assertFalse(self.device.connected)
            if self.try_connect():
                done = True
            elif self.error is not None:
                done = True
                err = self.error
                self.fail('connect({}) -> {}: {}'.format(self.device.remoteaddr(), str(err.__class__.__name__), str(err)))
            else:
                # assume hdmi2usbd isn't running
                rc = self.device.start_daemon()
                self.assertEqual(rc, 0)
