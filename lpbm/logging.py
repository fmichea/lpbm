# logging.py - Configures logging and workflow of the program.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import logging
import logging.handlers
import queue

_LOGGER_NAME = 'LPBM_LOGGER'
_LOGGER_BASIC_CONFIG = {
    'format': '[%(levelname)5s:%(lineno)3d] %(module)s.%(funcName)s: %(message)s',
    'level': logging.DEBUG,
}

_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
}

_FORMATTER = logging.Formatter(_LOGGER_BASIC_CONFIG['format'])

class WaitingConfigurationHandler(logging.handlers.MemoryHandler):
    def __init__(self):
        logging.handlers.MemoryHandler.__init__(self, 3)
        self.targets = []

    def setTargets(self, targets):
        self.targets = targets

    def flushAll(self):
        for target in self.targets:
            for record in self.buffer:
                target.emit(record)
        self.buffer = []

    def flush(self): pass

_TEMP_HANDLER = WaitingConfigurationHandler()

def get():
    return logging.getLogger(_LOGGER_NAME)

def init():
    logger = get()
    logger.setLevel(_LOGGER_BASIC_CONFIG['level'])

    logger.addHandler(_TEMP_HANDLER)
    _TEMP_HANDLER.setLevel(_LOGGER_BASIC_CONFIG['level'])

def configure(config):
    logger = get()
    logger.removeHandler(_TEMP_HANDLER)

    # Loading configuration
    handlers = []
    if 'logging-std' in config:
        handler = logging.StreamHandler()
        handler.setLevel(_LEVELS[config['logging-std'].get('level', 'DEBUG')])
        handlers.append(handler)

    _TEMP_HANDLER.setTargets(handlers)
    for handler in handlers:
        handler.setFormatter(_FORMATTER)
        logger.addHandler(handler)

    # Transfering previous message to newly configured logging module.
    _TEMP_HANDLER.flushAll()
