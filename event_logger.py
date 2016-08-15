"""
    Opsis/Atlys montor daemon: uses hdmi2usbd to communicate
"""
import sys
import argparse
import logging
import hdmi2usbmon as mon


class EventLogger(object):

    _logger = logging.getLogger(__name__)

    def __init__(self, *argv):
        self.args = None
        self.loglevel = logging.DEBUG
        self.options = argparse.Namespace()
        self.parse_args(*argv)
        self.log_init()

    def parse_args(self, *argv):
        parser = argparse.ArgumentParser()
        parser.add_argument('-H', '--host', default='localhost',
                            help="host to connect to hdmi2usbd")
        parser.add_argument('-P', '--port', type=int, default=8501,
                            help="tcp port to connect to hdmi2usbd")
        parser.add_argument('-p', '--program', type=str, dest='hdmi2usbd', default='hdmi2usbd',
                            help="full pathname to hdmi2usbd")
        parser.add_argument('-v', '--verbose', dest='verbose_count', action="count", default=1,
                            help="increases log verbosity for each occurence.")
        parser.add_argument('-o', '--output', type=argparse.FileType('w'), default=sys.stdout,
                            help="redirect log output to a file")
        self.args = parser.parse_args(args=argv, namespace=self.options)
        # Sets log level to WARN going more verbose for each new -v.
        self.logger.setLevel(max(3 - self.args.verbose_count, 0) * 10)

    @property
    def logger(self):
        return self._logger

    @logger.setter
    def logger(self, logger):
        self._logger = logger

    # Logging related functions

    def log_init(self):
        logging.basicConfig(stream=self.args.output, level=self.loglevel, format='%(asctime)s %(levelname)s %(message)s')

    def log_message(self, level, format_spec, *args, **kwargs):
        self.logger.log(level, format_spec, *args, **kwargs)

    def log_error(self, format_spec, *args, **kwargs):
        return self.log_message(logging.ERROR, format_spec, *args, **kwargs)

    def log_warn(self, format_spec, *args, **kwargs):
        return self.log_message(logging.WARNING, format_spec, *args, **kwargs)

    def log_info(self, format_spec, *args, **kwargs):
        return self.log_message(logging.INFO, format_spec, *args, **kwargs)

    def log_debug(self, format_spec, *args, **kwargs):
        return self.log_message(logging.DEBUG, format_spec, *args, **kwargs)

    # Run the logger

    def run(self):
        self.log_debug('Connecting to %s', self.args.hdmi2usbd)

        # do stuff
        pass


def main(*argv):
    logger = EventLogger(*(sys.argv[1:]))
    logger.log_info('EventLogger start')
    try:
        logger.run()
    except KeyboardInterrupt:
        logger.logger('Terminated by user interrupt')
    logger.log_info('EventLogger end')

if __name__ == '__main__':
    main(*sys.argv[1:])
