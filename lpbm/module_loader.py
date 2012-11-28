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
        self.needed_modules, self.module_loaded = None, False

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
        modules['config'].module_load(modules, args)
        for mod in self.needed_modules:
            modules[mod].module_load(modules, args)
        self.modules, self.args = modules, args
        self.module_load(modules, args)
        self.process(modules, args)

    def module_load(self, modules, args):
        if self.module_loaded:
            return
        self.module_loaded, self.args = True, args
        self.load(modules, args)

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


class ModelManagerModule(Module, metaclass=abc.ABCMeta):
    def __init__(self):
        super().__init__()
        self._objects = dict()
        self.fgroup, self.ggroup, self.igroup = None, None, None
        self.fopts, self.gopts, self.iopts = [], [], []
        self.helps = {
            'delete': 'Deletes the selected {object_name}.',
            'edit': 'Edit the {object_name}.',
            'id': 'Selects an {object_name} for several options.',
            'list': 'List all the {object_name_plural}.',
            'new': 'Adds a new {object_name} interactively.',
            'with-deleted': 'Includes deleted {object_name_plural} in listings.',
        }

    def __getitem__(self, id):
        try:
            return self._objects[id]
        except KeyError:
            raise lpbm.exceptions.ModelDoesNotExistError(self.object_name(), id)

    def create_object(self, cls, *args, **kwargs):
        return cls(self, self.modules, *args, **kwargs)

    def register_object(self, cls, *args, **kwargs):
        obj = self.create_object(cls, *args, **kwargs)
        self._objects[obj.id] = obj
        return obj

    @property
    def objects(self):
        return [obj for obj in self._objects.values()
                if self.args.with_deleted or not obj.deleted]

    @property
    def all_objects(self):
        return list(self._objects.values())

    def init(self):
        # Set correctly object name to its value.
        kwargs = {
            'object_name': self.object_name(),
            'object_name_plural': self.object_name_plural(),
        }
        self.helps = dict((k, v.format(**kwargs)) for (k, v) in self.helps.items())

        # Default options.
        self.parser.add_argument('-i', '--id', action='store', type=int,
                                 metavar='id', default=None, help=self.helps['id'])

        self.ggroup = self.parser.add_argument_group(title='general actions')
        self.add_general_option('-n', '--new', help=self.helps['new'])
        self.add_general_option('-l', '--list', help=self.helps['list'])

        self.fgroup = self.parser.add_argument_group(title='flags')
        self.add_flag_option('-D', '--with-deleted', help=self.helps['with-deleted'])

        self.igroup = self.parser.add_argument_group(title='specific actions (need --id)')
        self.add_id_option('-e', '--edit', help=self.helps['edit'])
        self.add_id_option('-d', '--delete', help=self.helps['delete'])

    def _add_option(self, group, opts, args, kwargs_):
        opts.append(kwargs_.get('dest', sorted(args, key=len)[-1][2:]))
        kwargs = {'default': None, 'action': 'store_true'}
        kwargs.update(kwargs_)
        group.add_argument(*args, **kwargs)

    def add_flag_option(self, *args, **kwargs):
        self._add_option(self.fgroup, self.fopts, args, kwargs)

    def add_general_option(self, *args, **kwargs):
        self._add_option(self.ggroup, self.gopts, args, kwargs)

    def add_id_option(self, *args, **kwargs):
        self._add_option(self.igroup, self.iopts, args, kwargs)

    def process(self, modules, args):
        def option_mangle(opt):
            return opt.replace('-', '_')
        def option_states(opts):
            return dict((k, getattr(args, option_mangle(k))) for k in opts)

        # First check general options.
        opts_states = option_states(self.gopts)
        for opt, state in opts_states.items():
            if state is not None:
                try:
                    getattr(self, 'opt_' + opt)()
                    return
                except (AttributeError, TypeError):
                    raise lpbm.exceptions.GeneralOptionError(opt)

        # If we have any id option in there.
        opts_states = option_states(self.iopts)
        for opt, state in opts_states.items():
            if state is not None:
                if args.id is None:
                    raise lpbm.exceptions.IdOptionMissingError(opt)
                try:
                    getattr(self, 'opt_' + opt)(args.id)
                    return
                except (AttributeError, TypeError):
                    raise lpbm.exceptions.IdOptionError(opt)

        self.parser.print_help()

    # Actions.
    def opt_list(self, short=False):
        if not short:
            print('All {object_name}s:'.format(object_name=self.object_name()))
        for obj in self.objects:
            print(' {id:2d} - {obj}{deleted}'.format(
                id=obj.id, obj=obj,
                deleted=' [deleted]' if obj.deleted else '',
            ))

    def opt_new(self, *args, **kwargs):
        obj = self.create_object(self.model_cls(), *args, **kwargs)
        obj.interactive()
        obj.save()
        self._objects[obj.id] = obj
        return obj

    def opt_edit(self, id):
        obj = self[id]
        obj.interactive()
        obj.save()

    def opt_delete(self, id):
        obj = self[id]
        obj.delete()
        obj.save()

    @abc.abstractmethod
    def object_name(self):
        pass

    @abc.abstractmethod
    def model_cls(self):
        pass

    def object_name_plural(self):
        return self.object_name() + 's'

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
                    except TypeError as e:
                        msg = '  -> Failed to instanciate class %s, abstract '
                        msg += 'method or property missing?'
                        logger.debug(msg, item[0])
                        logger.debug('    Error: ' + str(e))
        except ImportError as err:
            logger.debug('Failed to import module %s (%s).', mod_name, err)
