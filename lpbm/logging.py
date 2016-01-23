# logging.py - Configures logging and workflow of the program.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
This module can be used everywhere to log data. It is activated with command
line option.
'''

import logging
import logging.handlers

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
    '''This class keeps logs in memory until we have a configuration.'''

    def __init__(self):
        '''We initialize a memory handler with no targets.'''
        logging.handlers.MemoryHandler.__init__(self, 3)
        self.targets = []

    def setTargets(self, targets):
        '''We can reset targets whenever we want.'''
        self.targets = targets

    def flushAll(self):
        '''For all targets, we send the buffer.'''
        for target in self.targets:
            for record in self.buffer:
                target.emit(record)
        self.buffer = []

    def flush(self):
        pass


_TEMP_HANDLER = WaitingConfigurationHandler()


def get():
    '''Returns global logger to be used everywhere.'''
    return logging.getLogger(_LOGGER_NAME)


def init():
    '''
    Sends basic configuration to the logger to wait for more info from the
    command line.i
    '''
    logger = get()
    logger.setLevel(_LOGGER_BASIC_CONFIG['level'])

    logger.addHandler(_TEMP_HANDLER)
    _TEMP_HANDLER.setLevel(_LOGGER_BASIC_CONFIG['level'])


def configure(config):
    '''
    When we finally have the full configuration, we can reconfigure logger.
    '''
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
