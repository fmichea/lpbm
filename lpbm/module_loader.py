# module_loader.py - Loads every module in tools directory.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
This module dynamically loads all the command line modules in `modules`
directory.
'''

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

    def __init__(self):
        self.parser, self.modules, self.args = None, None, None
        self.needed_modules = None

    def module_init(self, argument_parser):
        """
        This function initialize a parser for the command line. It also,
        initialize needed module to none (empty list). If you want to load data
        from other modules, you should override this in your init function.
        """
        self.parser = argument_parser.add_parser(
            self.name(), help=self.abstract(), description=self.abstract()
        )
        self.parser.set_defaults(func=self.module_process)
        self.needed_modules = []
        self.init()

    def module_process(self, modules, args):
        """
        This methods calls the load function of each needed module and then
        calls the process function overriden by you. Configuration is always
        loaded.
        """
        modules['config'].load(modules, args)
        for mod in self.needed_modules:
            modules[mod].load(modules, args)
        self.modules, self.args = modules, args
        self.load(modules, args)
        self.process(modules, args)

    @abc.abstractmethod
    def init(self):
        """
        This function should add its own arguments on command line. When
        called, self.parser will be initialized with a valid argument parser.
        """
        pass

    def load(self, modules, args):
        """
        This function can be overriden to load data according to global
        arguments. It can be overriden.
        """
        pass

    @abc.abstractmethod
    def name(self):
        """Returns the name of the parser on command line."""
        pass

    @abc.abstractmethod
    def abstract(self):
        """Returns an abstract of the functionnality of the command."""
        pass

    @abc.abstractmethod
    def process(self, modules, args):
        """Invoked if command was chosen on command line."""
        pass

def load_modules(modules_, argument_parser):
    """Dynamically loads all the compatible commands from modules directory"""
    main_root = os.path.join(os.path.dirname(__file__), 'modules')
    logger, modules = lpbm.logging.get(), []

    # Finds all submodules that should be loaded.
    logger.debug('Tool being loaded from %s.', main_root)
    for root, _, files in os.walk(main_root):
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

    modules = sorted(modules, key=lambda mod: mod[0])

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
                        msg = 'Command %s was correctly loaded.'
                        logger.info(msg, tmp.name())
                        modules_[tmp.name()] = tmp
                    except TypeError:
                        msg = '  -> Failed to instanciate class %s, abstract '
                        msg += 'method or property missing?'
                        logger.debug(msg, item[0])
        except ImportError as err:
            logger.debug('Failed to import module %s (%s).', mod_name, err)
