# lpbm/exceptions.py - All the errors that can be raised in the program.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)


class GeneralOptionError(Exception):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        msg = 'Could not find or call any function for `--{}` options.'
        return msg.format(self.name)


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
        return 'Cannot assign read-only value.'


class FieldRequiredError(Exception):
    def __str__(self):
        return 'Field is required and cannot be set to empty value None.'


class ConfigOptionArgsError(Exception):
    def __str__(self):
        msgs = [
            'ConfigOptionField.__init__ takes one or two arguments.',
            'See documentation for more details.',
        ]
        return ' '.join(msgs)


# Model Errors


class AttributeNotAFieldError(Exception):
    def __init__(self, attr_name):
        self.attr_name = attr_name

    def __str__(self):
        msg = 'Attribute `{attr_name}` is not a field. You must implement '
        msg += '`interactive_{attr_name}` if you want it to be interactive.'
        return msg.format(attr_name=self.attr_name)


class ModelDoesNotExistError(Exception):
    def __init__(self, object_name, id):
        self.object_name, self.id = object_name, id

    def __str__(self):
        return 'There is no such {object_name} (id = {id}).'.format(
            object_name=self.object_name, id=self.id
        )
