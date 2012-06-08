# module_loader.py - Loads every module in tools directory.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import imp
import inspect
import os
import sys

import lpbm.logging

from lpbm.modules import Module

def load_modules(commands, argument_parser):
    main_root = os.path.join(os.path.dirname(__file__), 'tools')
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
                        tmp.init(argument_parser)
                        if tmp.name() in commands:
                            msg = 'A command already uses name %s.'
                        else:
                            commands[tmp.name()] = tmp
                            msg = 'Command %s was correctly loaded.'
                        logger.info(msg, tmp.name())
                    except TypeError:
                        msg = '  -> Failed to instanciate class %s, abstract '
                        msg += 'method or property missing?'
                        logger.debug(msg, item[0])
        except ImportError:
            logger.debug('Failed to load module %s.', mod_name)
