import operator

import lpbm.v3.lib.dict_utils as _dict_utils

from lpbm.v3.lib.model.errors import (
    ModelFieldMissingError,
    ModelFieldReadOnlyError,
)
from lpbm.v3.lib.model.field_bool_op import ModelFieldTest


class ModelField(object):
    def __init__(self, path, read_only=False):
        self.path, self.path_sp = path, path.split('.')
        self.read_only = read_only

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        return self.get(instance)

    def get(self, instance):
        try:
            return _dict_utils.get_value(instance._data, self.path_sp)
        except KeyError:
            msg = 'field not found {0}'.format(self.path)
            raise ModelFieldMissingError(msg)

    def __set__(self, instance, value):
        self.set(instance, value)

    def set(self, instance, value):
        if self.read_only:
            raise ModelFieldReadOnlyError(self.path)
        _dict_utils.set_value(instance._data, self.path_sp, value)

    def __delete__(self, instance):
        self.delete(instance)

    def delete(self, instance):
        # FIXME: deleting a required field with a default value should reest to
        # the default value.
        _dict_utils.delete_value(instance._data, self.path_sp)

    def __eq__(self, other):
        return ModelFieldTest(operator.eq, self, other)

    def __ne__(self, other):
        return ModelFieldTest(operator.ne, self, other)
