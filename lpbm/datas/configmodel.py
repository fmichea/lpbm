# configmodel.py - Model to manipulate configuration.
# Author(s): Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import configparser


class ConfigOptionDescriptor:
    '''
    Maps a value in a configuration to be able to get and set it blindly. If
    `a` maps section 'foo' and option 'bar'. You can use `a` like this:

        a = 1 # sets foo.bar ([foo] option bar) to 1.
        b = a # gets foo.bar ([foo] option bar) (here 1).
    '''

    def __init__(self, section, option, **kwargs):
        # Private attributes.
        self._section, self._option = section, option
        self._default = kwargs.get('default', None)
        self._read_only = kwargs.get('read_only', False)

    def __set__(self, instance, val):
        cfg = instance.cm.config
        if self._read_only:
            return
        if not cfg.has_section(self._section):
            cfg.add_section(self._section)
        if val is None:
            cfg.remove_option(self._section, self._option)
        else:
            cfg.set(self._section, self._option, str(val))

    def __get__(self, instance, type=None):
        getter, cfg = self._getter_function(), instance.cm.config
        if getter is None:
            getter = configparser.ConfigParser.get
        value = getter(cfg, self._section, self._option, fallback=None)
        if value is None and self._default is not None:
            value = self._default
            self.__set__(instance, self._default)
        return value

    def _getter_function(self):
        return None


class ConfigOptionDescriptorBoolean(ConfigOptionDescriptor):
    def _getter_function(self):
        return configparser.ConfigParser.getboolean

    def __set__(self, obj, val):
        val = 'yes' if val else 'no'
        super(ConfigOptionDescriptorBoolean, self).__set__(obj, val)


class ConfigOptionDescriptorInt(ConfigOptionDescriptor):
    def _getter_function(self):
        return configparser.ConfigParser.getint


class ConfigOptionDescriptorFloat(ConfigOptionDescriptor):
    def _getter_function(self):
        return configparser.ConfigParser.getfloat


class ConfigModel:
    def __init__(self, filename):
        self.config, self._filename = configparser.ConfigParser(), filename
        self.config.read(filename, encoding='utf-8')

    def __del__(self):
        with codecs.open(self._filename, 'w', 'utf-8') as file_descriptor:
            self.config.write(file_descriptor)


def opt(sect, opt, **kwargs):
    return ConfigOptionDescriptor(sect, opt, **kwargs)

def opt_int(sect, opt, **kwargs):
    return ConfigOptionDescriptorInt(sect, opt, **kwargs)

def opt_bool(sect, opt, **kwargs):
    return ConfigOptionDescriptorBoolean(sect, opt, **kwargs)

def opt_float(sect, opt, **kwargs):
    return ConfigOptionDescriptorFloat(sect, opt, **kwargs)
