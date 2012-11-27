# lpbm/exceptions.py - All the errors that can be raised in the program.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)


class GeneralOptionError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Couldn\'t find or call any function for `--{}` options.'.format(
            self.name
        )


class IdOptionError(GeneralOptionError):
    pass


class IdOptionMissingError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return 'Id must be precised when using option `--{}`.'.format(self.name)


class ObjectNotFound(Exception):
    def __init__(self, id, name):
        self.id, self.name = id, name

    def __str__(self):
        return 'There is no {} with this id ({}).'.format(self.name, self.id)


# Field Errors

class FieldReadOnlyError(Exception):
    def __str__(self):
        return 'Can\'t assign read-only value.'

class FieldRequiredError(Exception):
    def __str__(self):
        return 'Field is required and can\'t be set to empty value None.'

class ConfigOptionArgsError(Exception):
    def __str__(self):
        return 'ConfigOptionField.__init__ takes one or two arguments. See ' \
               'documentation for more details.'

# Model Errors
class AttributeNotAFieldError(Exception):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __str__(self):
        return 'Attribute `{attr_name}` is not a field. You must implement ' \
               '`interactive_{attr_name}` if you want it to be interactive.'.format(
            attr_name = self.attr_name,
        )
