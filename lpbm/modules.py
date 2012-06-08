# modules.py - Loads every module in tools directory.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import abc

class Module(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def init(self, argument_parser): pass

    @abc.abstractmethod
    def name(self): pass

    @abc.abstractmethod
    def process(self): pass
