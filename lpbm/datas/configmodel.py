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

    def __get__(self, instance, type=None):
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

    # FIXME: probably shouldn't do this.
    def __del__(self):
        self.save()

    def save(self):
        with codecs.open(self._filename, 'w', 'utf-8') as file_descriptor:
            self.config.write(file_descriptor)


def opt(*args, **kwargs):
    return ConfigOptionDescriptor(*args, **kwargs)

def opt_int(*args, **kwargs):
    return ConfigOptionDescriptorInt(*args, **kwargs)

def opt_bool(*args, **kwargs):
    return ConfigOptionDescriptorBoolean(*args, **kwargs)

def opt_float(*args, **kwargs):
    return ConfigOptionDescriptorFloat(*args, **kwargs)
