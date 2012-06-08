# module_loader.py - Loads every module in tools directory.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import abc
import imp
import inspect
import os
import sys

import lpbm.logging

class Module(metaclass=abc.ABCMeta):
    """
    This is the base class of all modules. You can find documentation for every
    method required. To create a new module, you just have to create an new
    file in modules directory, inheriting from this class, and implementing
    following methods. It will then be loaded automatically.
    """

    def module_init(self, argument_parser):
        self.parser = argument_parser.add_parser(self.name(), help=self.abstract())
        self.parser.set_defaults(func=self.process)

    @abc.abstractmethod
    def init(self):
        """
        This function should add its own arguments on command line. When
        called, self.parser will be initialized with a valid argument parser.
        """
        pass

    @abc.abstractmethod
    def name(self):
        """Returns the name of the parser on command line."""
        pass

    def abstract(self):
        """Returns an abstract of the functionnality of the command."""
        pass

    @abc.abstractmethod
    def process(self, args):
        """Invoked if command was chosen on command line."""
        pass

def load_modules(argument_parser):
    """Dynamically loads all the compatible commands from modules directory"""
    main_root = os.path.join(os.path.dirname(__file__), 'modules')
    logger, modules = lpbm.logging.get(), []

    # Finds all submodules that should be loaded.
    logger.debug('Tool being loaded from %s.', main_root)
    for root, dirs, files in os.walk(main_root):
        root_ = root[len(main_root):]
        for filename in files:
            if not filename.endswith('.py'):
                continue
            mod_name = root_.replace('/', '.') + filename[:-3]
            try:
                modules.append((
                    mod_name, imp.find_module(mod_name, [root] + sys.path)
                ))
                logger.debug('Module found: lpbm.tools.%s', mod_name)
            except ImportError:
                logger.debug('Failed to find module %s.', mod_name)

    # Loads modules 1 by 1.
    for mod_name, (fd, pathname, description) in modules:
        try:
            mod = imp.load_module(mod_name, fd, pathname, description)
            logger.debug('Module loaded: %s', mod.__name__)
            for item in inspect.getmembers(mod):
                logger.debug(' + Item in module found: %s', item[0])
                if inspect.isclass(item[1]) and issubclass(item[1], Module):
                    try:
                        logger.debug('  -> Item is a subclass of Module class.')
                        tmp = item[1]()
                        tmp.module_init(argument_parser)
                        tmp.init()
                        msg = 'Command %s was correctly loaded.'
                        logger.info(msg, tmp.name())
                    except TypeError:
                        msg = '  -> Failed to instanciate class %s, abstract '
                        msg += 'method or property missing?'
                        logger.debug(msg, item[0])
        except ImportError:
            logger.debug('Failed to load module %s.', mod_name)
