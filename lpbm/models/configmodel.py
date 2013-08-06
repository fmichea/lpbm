# configmodel.py - Model to manipulate configuration.
# Author(s): Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
This module exports a descriptor helper that helps getting and setting values
in ini files like normal attributes of an object.
'''

import codecs
import configparser

import lpbm.tools as ltools
import lpbm.exceptions

class BaseField:
    def __init__(self, **kwargs):
        # Options all fields should have,
        self.default = kwargs.get('default', None)
        self.read_only = kwargs.get('read_only', False)
        self.required = kwargs.get('required', False)
        self.verbose_name = kwargs.get('verbose_name', None)


class ValueField(BaseField):
    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self._name = name

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        return getattr(instance, self._mangled_name(), self.default)

    def __set__(self, instance, value):
        if self.read_only:
            raise lpbm.exceptions.FieldReadOnlyError()
        if self.required and value is None:
            if self.default is not None:
                value = self.default
            else:
                raise lpbm.exceptions.FieldRequiredError()
        setattr(instance, self._mangled_name(), value)

    def _mangled_name(self):
        return '_{}_{}'.format(self.__class__, self._name)


# pylint: disable=R0903
class ConfigOptionField(BaseField):
    def __init__(self, *args, **kwargs):
        super().__init__(**kwargs)

        # Private attributes.
        if len(args) == 1:
            self._section, self._option = None, args[0]
        elif len(args) == 2:
            self._section, self._option = args
        else:
            raise lpbm.exception.ConfigOptionArgsError(text)

    def __set__(self, instance, val):
        cfg = instance.cm.config
        if self.read_only:
            raise lpbm.exceptions.AssignFieldReadOnlyError()
        section = self._section or instance.section
        if not cfg.has_section(section):
            cfg.add_section(section)
        if val is None:
            cfg.remove_option(section, self._option)
        else:
            cfg.set(section, self._option, str(val))

    def __get__(self, instance, type_=None):
        if instance is None:
            return self
        try:
            getter, cfg = self._getter_function(), instance.cm.config
            if getter is None:
                getter = configparser.ConfigParser.get
            section = self._section or instance.section
            value = getter(cfg, section, self._option, fallback=None)
            if value is None and self.default is not None:
                value = self.default
                self.__set__(instance, value)
        except AttributeError:
            value = self.default
        return value

    # pylint: disable=R0201
    def _getter_function(self):
        '''
        Override this method to change the configparser's function getting
        the value in configuration.
        '''
        return None

# pylint: disable=R0903
class ConfigOptionFieldBoolean(ConfigOptionField):
    '''ConfigOptionField returning and setting booleans.'''

    def _getter_function(self):
        return configparser.ConfigParser.getboolean

    # pylint: disable=E1002
    def __set__(self, obj, val):
        val = 'yes' if val else 'no'
        super(ConfigOptionFieldBoolean, self).__set__(obj, val)

    def _getter_type(self):
        class DataBool(Data):
            def __init__(self, val):
                self._value = val
            def __bool__(self):
                return self._value
        return DataBool


# pylint: disable=R0903
class ConfigOptionFieldInt(ConfigOptionField):
    '''ConfigOptionField returning and setting ints.'''

    def _getter_function(self):
        return configparser.ConfigParser.getint

    def _getter_type(self):
        return data_factory(int)


# pylint: disable=R0903
class ConfigOptionFieldFloat(ConfigOptionField):
    '''ConfigOptionField returning and setting floats.'''

    def _getter_function(self):
        return configparser.ConfigParser.getfloat

    def _getter_type(self):
        return data_factory(float)


# pylint: disable=R0903
class ConfigModel:
    '''
    This is the actual class, which instances contain a configuration. It's
    only there to keep filename of configuration for opening and closing.
    '''

    def __init__(self, filename):
        self.config, self.filename = configparser.ConfigParser(), filename
        self.config.read(filename, encoding='utf-8')

    def save(self):
        '''Saves configuration in its original file.'''
        with codecs.open(self.filename, 'w', 'utf-8') as f:
            self.config.write(f)


def field(*args, **kwargs):
    return ValueField(*args, **kwargs)

def opt(*args, **kwargs):
    '''Returns an instance of ConfigOptionField (manipulating string).'''
    return ConfigOptionField(*args, **kwargs)

def opt_int(*args, **kwargs):
    '''Returns an instance of ConfigOptionFieldInt.'''
    return ConfigOptionFieldInt(*args, **kwargs)

def opt_bool(*args, **kwargs):
    '''Returns an instance of ConfigOptionFieldBoolean.'''
    return ConfigOptionFieldBoolean(*args, **kwargs)

def opt_float(*args, **kwargs):
    '''Returns an instance of ConfigOptionFieldFloat.'''
    return ConfigOptionFieldFloat(*args, **kwargs)

class Model:
    id = opt_int('id')
    deleted = opt_bool('deleted', default=False)

    def __init__(self, mod, mods):
        self.cm, self.mod, self.mods, self.__id = None, mod, mods, None
        self._interactive_fields = []

    def interactive(self):
        fields = ['id'] + list(self._interactive_fields)
        try:
            fields.insert(fields.index('section') + 1, 'id')
        except ValueError:
            pass
        for attr_name in fields:
            try:
                method = getattr(self, 'interactive_' + attr_name)
            except AttributeError:
                self._interactive_field(attr_name)
                continue
            method()

    def _interactive_field(self, attr_name):
        def prompt_name(attr_name):
            return attr_name.replace('_', ' ').title()
        attr = getattr(self, attr_name)
        attr_class = getattr(type(self), attr_name, None)
        if isinstance(attr_class, BaseField):
            prompt = getattr(attr_class, 'verbose_name') or prompt_name(attr_name)
            tmp = 'interactive_' + attr_name + '_is_valid'
            kwargs = {
                'required': attr_class.required,
                'is_valid': getattr(self, tmp, None),
            }
            setattr(self, attr_name, ltools.input_default(prompt, attr, **kwargs))
        else:
            raise lpbm.exceptions.AttributeNotAFieldError(attr_name)

    def interactive_id(self):
        if self.id is None and self.__id is None:
            ids = [o.id for o in self.mod.all_objects]
            def is_valid(val):
                try:
                    val = int(val)
                except ValueError:
                    return False
                return val not in ids
            try:
                default = max(ids) + 1
            except ValueError:
                default = 0
            id = ltools.input_default('Id', default, required=True, is_valid=is_valid)
            if 'section' in self._interactive_fields:
                self.__id = id
            else:
                self.id = id
        elif self.__id is not None:
            self.id = self.__id

    def save(self):
        self.cm.save()

    def delete(self):
        self.deleted = True

    def list_verbose(self):
        return str(self)

    @property
    def section(self):
        return 'general'
