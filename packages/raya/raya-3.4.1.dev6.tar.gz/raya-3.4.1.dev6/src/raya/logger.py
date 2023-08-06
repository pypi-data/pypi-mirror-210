import logging
import logging.config


class ColorFormatter(logging.Formatter):

    def format(self, record):
        return


def create_logger(name: str):
    pass


__deprecation_logger = create_logger('Deprecation Notice')
__debug_warning_logger = create_logger('Debug')


def DEPRECATION_WARNING(msg):
    pass


def DEBUG_WARNING(msg):
    pass
