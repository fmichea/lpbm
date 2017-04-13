from voluptuous.error import MultipleInvalid as _MultipleInvalid

from lpbm.v3.lib import dict_utils as _dict_utils
from lpbm.v3.lib.model.base import BaseModel, is_model, model_name
from lpbm.v3.lib.model.errors import (
    ModelInvalidError,
    ModelNoParentDefinedError,
    ModelParentAlreadySetError,
    ModelParentTypeError,
)
from lpbm.v3.lib.model.meta import ModelMeta
from lpbm.v3.lib.model.ref import is_model_ref
from lpbm.v3.lib.model.types.base import is_custom_type


class Model(BaseModel, metaclass=ModelMeta):
    __lpbm_config__ = {
        'schema': {},
        'filename_pattern': None,
    }

    def __init__(self, data=None, session=None, parent=None):
        if data is not None:
            # Raw data given to model must pass schema check. We need to
            # translate all the data into in-memory format.
            def _translate_from_raw_data(full_path, key, val):
                key_info = self._schema().key_info.get(full_path)
                if key_info is None:
                    return val
                type_ = key_info.T
                if is_model(type_):
                    return type_(data=val)
                elif isinstance(type_, list) and is_model(type_[0]):
                    return [type_[0](x) for x in val]
                elif is_custom_type(type_):
                    return type_.load(session, self, val)
                elif isinstance(type_, list) and is_custom_type(type_[0]):
                    return [type_[0].load(session, self, v) for v in val]
                return val
            try:
                data = _dict_utils.map(self._schema()(data), _translate_from_raw_data)
            except _MultipleInvalid as exc:
                raise ModelInvalidError(self, str(exc))
        else:
            data = dict()
            for key, val in self._schema().data_defaults.items():
                _dict_utils.set_value(data, key.split('.'), val())

        self._data = data

        self._parent = None
        if parent is not None:
            self.parent = parent

        self._ref = {'clsname': model_name(self)}

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        if self._parent is not None:
            raise ModelParentAlreadySetError(self, 'parent already set')
        parent_cfg = self._filename_pattern('parent')
        if parent_cfg is None:
            raise ModelNoParentDefinedError(self, 'no parent defined')
        if not isinstance(val, parent_cfg['class']):
            err = 'type {0} is not expected parent type {1}'
            err = err.format(type(val).__name__, parent_cfg['class'].__name__)
            raise ModelParentTypeError(self, err)
        self._parent = val

    def __repr__(self):
        val = super().__repr__()
        if hasattr(self, 'uuid'):
            val = '{0} with uuid={1}>'.format(val[:-1], self.uuid)
        return val

    def validate(self, session=None):
        # FIXME: self.as_dict(session=session)
        pass

    def ref(self):
        self._ref.update({
            'clsname': model_name(self),
            'uuid': self.uuid,
        })
        self._ref.update(self._parents_refs_uuid())
        return self._ref

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self.as_dict() == other.as_dict()
        )

    def as_dict(self, session=None):
        """
        This function returns the on-disk representation of this model. It is
        not safe to modify the value returned by this function in any way. This
        function is mostly internal and should be avoided.
        """
        def _translate_to_raw_data(full_path, key, val):
            key_info = self._schema().key_info.get(full_path)
            if key_info is None:
                return val
            type_ = key_info.T
            if is_model(type_):
                return val.as_dict(session=session)
            elif isinstance(type_, list) and is_model(type_[0]):
                return [v.as_dict(session=session) for v in val]
            elif is_custom_type(type_) and val is not None:
                return type_.dump(session, self, val)
            elif isinstance(type_, list) and is_custom_type(type_[0]):
                return [type_[0].dump(session, self, v) for v in val]
            return val
        tmp = _dict_utils.map(self._data, _translate_to_raw_data)

        try:
            return self._schema()(tmp)
        except _MultipleInvalid as exc:
            raise ModelInvalidError(self, str(exc))

    @classmethod
    def _parents_uuids(cls):
        parent = cls._filename_pattern('parent')
        if parent is None:
            return []
        parents = ['{0}_uuid'.format(parent['name'])]
        parents.extend(parent['class']._parents_uuids())
        return parents

    def _parents_refs(self):
        parent = self.parent
        if parent is None:
            return {}
        result = {self._filename_pattern('parent')['name']: parent}
        result.update(parent._parents_refs())
        return result

    def _parents_refs_uuid(self):
        return {
            '{0}_uuid'.format(k): v.uuid
            for k, v in self._parents_refs().items()
        }

    def _model_filename(self):
        kw = self._parents_refs_uuid()
        kw.update({'uuid': self.uuid})

        filename_pattern = self._filename_pattern('full_pattern')
        return filename_pattern.format(**kw)

    def filenames(self):
        return [self._model_filename()]

    @classmethod
    def _schema(cls):
        return cls.__lpbm_config__['schema']

    @classmethod
    def _filename_pattern(cls, item):
        filename_pattern = cls.__lpbm_config__.get('filename_pattern')
        if filename_pattern is None:
            return None
        return filename_pattern[item]
