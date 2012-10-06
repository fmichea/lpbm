# configmodel.py - Model to manipulate configuration.
# Author(s): Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
This module exports a descriptor helper that helps getting and setting values
in ini files like normal attributes of an object.
'''

import codecs
import configparser

# pylint: disable=R0903
class ConfigOptionDescriptor:
    '''
    Maps a value in a configuration to be able to get and set it blindly. If
    `a` maps section 'foo' and option 'bar'. You can use `a` like this:

        a = 1 # sets foo.bar ([foo] option bar) to 1.
        b = a # gets foo.bar ([foo] option bar) (here 1).

    Constructor take one or two "normal" arguments, depending of the behavior
    you want to achieve. Both should be strings. If you give two parameters,
    then you give section_name as first paramter, and option_name as second. If
    you only give one, it's option_name and section_name will be retreived by
    getting section property of the instance.

    You can subclass this descriptor for types. Basic types managed by
    configparser are builtin implemented in module. You have function to help
    you create them with a shorter name.
    '''

    def __init__(self, *args, **kwargs):
        # Private attributes.
        if len(args) == 1:
            self._section, self._option = None, args[0]
        elif len(args) == 2:
            self._section, self._option = args
        else:
            text = 'ConfigOptionDescriptor.__init__ takes one or two '
            text += 'arguments. Section and option names, OR only option '
            text += 'name.'
            raise TypeError(text)
        self._default = kwargs.get('default', None)
        self._read_only = kwargs.get('read_only', False)

    def __set__(self, instance, val):
        cfg = instance.cm.config
        if self._read_only:
            return
        section = self._section or instance.section
        if not cfg.has_section(section):
            cfg.add_section(section)
        if val is None:
            cfg.remove_option(section, self._option)
        else:
            cfg.set(section, self._option, str(val))

    def __get__(self, instance):
        try:
            getter, cfg = self._getter_function(), instance.cm.config
        except AttributeError:
            return self._default
        if getter is None:
            getter = configparser.ConfigParser.get
        section = self._section or instance.section
        value = getter(cfg, section, self._option, fallback=None)
        if value is None and self._default is not None:
            value = self._default
            self.__set__(instance, self._default)
        return value

    # pylint: disable=R0201
    def _getter_function(self):
        '''
        Override this method to change the configparser's function getting
        the value in configuration.
        '''
        return None


# pylint: disable=R0903
class ConfigOptionDescriptorBoolean(ConfigOptionDescriptor):
    '''ConfigOptionDescriptor returning and setting booleans.'''

    def _getter_function(self):
        return configparser.ConfigParser.getboolean

    # pylint: disable=E1002
    def __set__(self, obj, val):
        val = 'yes' if val else 'no'
        super(ConfigOptionDescriptorBoolean, self).__set__(obj, val)


# pylint: disable=R0903
class ConfigOptionDescriptorInt(ConfigOptionDescriptor):
    '''ConfigOptionDescriptor returning and setting ints.'''

    def _getter_function(self):
        return configparser.ConfigParser.getint


# pylint: disable=R0903
class ConfigOptionDescriptorFloat(ConfigOptionDescriptor):
    '''ConfigOptionDescriptor returning and setting floats.'''

    def _getter_function(self):
        return configparser.ConfigParser.getfloat


# pylint: disable=R0903
class ConfigModel:
    '''
    This is the actual class, which instances contain a configuration. It's
    only there to keep filename of configuration for opening and closing.
    '''

    def __init__(self, filename):
        self.config, self._filename = configparser.ConfigParser(), filename
        self.config.read(filename, encoding='utf-8')

    def save(self):
        '''Saves configuration in its original file.'''
        with codecs.open(self._filename, 'w', 'utf-8') as f:
            self.config.write(f)


def opt(*args, **kwargs):
    '''Returns an instance of ConfigOptionDescriptor (manipulating string).'''
    return ConfigOptionDescriptor(*args, **kwargs)

def opt_int(*args, **kwargs):
    '''Returns an instance of ConfigOptionDescriptorInt.'''
    return ConfigOptionDescriptorInt(*args, **kwargs)

def opt_bool(*args, **kwargs):
    '''Returns an instance of ConfigOptionDescriptorBoolean.'''
    return ConfigOptionDescriptorBoolean(*args, **kwargs)

def opt_float(*args, **kwargs):
    '''Returns an instance of ConfigOptionDescriptorFloat.'''
    return ConfigOptionDescriptorFloat(*args, **kwargs)
