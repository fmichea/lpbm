import os
import yaml
import hashlib

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
from lpbm.v3.lib.model.owner_tracker import OwnerTracker
from lpbm.v3.lib.model.ref import is_model_ref
from lpbm.v3.lib.model.session_actions import CopyFileAction
from lpbm.v3.lib.model.types.base import is_custom_type
from lpbm.v3.lib.tmp import tempfile


def _hash_data(data):
    data_hash = hashlib.sha1()
    data_hash.update(data.encode('utf-8'))
    return data_hash.hexdigest()


class Model(BaseModel, metaclass=ModelMeta):
    __lpbm_config__ = {
        'schema': {},
        'filename_pattern': None,
    }

    def __init__(self, data=None, data_hash=None, session=None, owners=None, parent=None):
        if owners is None:
            owners = OwnerTracker()

        self._parent = None
        if parent is not None:
            self.parent = parent

        if data is not None:
            # Raw data given to model must pass schema check. We need to
            # translate all the data into in-memory format.
            def _translate_from_raw_data(full_path, key, val):
                key_info = self._schema().key_info.get(full_path)
                if key == 'category':
                    print(key, val)
                if val is None:
                    return val
                if key_info is None:
                    return val
                type_ = key_info.T
                if is_model(type_):
                    return type_(data=val, owners=owners)
                elif isinstance(type_, list) and is_model(type_[0]):
                    return [type_[0](data=x, owners=owners) for x in val]
                elif is_custom_type(type_):
                    return type_.load(session, owners, val)
                elif isinstance(type_, list) and is_custom_type(type_[0]):
                    return [type_[0].load(session, owners, v) for v in val]
                return val

            try:
                with owners.wrap(self):
                    self._data = data
                    data = _dict_utils.map(self._schema()(data), _translate_from_raw_data)
            except _MultipleInvalid as exc:
                raise ModelInvalidError(self, str(exc))

        else:
            data = dict()
            for key, val in self._schema().data_defaults.items():
                _dict_utils.set_value(data, key.split('.'), val())

        self._data = data
        self._data_hash = data_hash

        self._session = session

    @classmethod
    def load(cls, session, filename, parent=None):
        with open(session.in_blog_join(filename)) as fd:
            contents = fd.read()

        data_hash = _hash_data(contents)
        data = cls._schema()(yaml.safe_load(contents))

        return cls(data=data, data_hash=data_hash, session=session, parent=parent)

    def dump(self, session):
        dict_content = self.as_dict(session=session)

        contents = yaml.safe_dump(dict_content, default_flow_style=False)
        if _hash_data(contents) == self._data_hash:
            return

        path = tempfile()
        with open(path, 'w') as fd:
            fd.write(contents)

        session.add_commit_action(CopyFileAction(path, self._model_filename()))

    def __repr__(self):
        val = super().__repr__()
        if self.is_in_file_model():
            val = '{prefix} with uuid={uuid}>'.format(
                prefix=val[:-1], uuid=self.uuid)
        return val

    def __eq__(self, other):
        # FIXME: there is a problem here comparing in-file models which need a
        # session to to as_dict() on due to references.
        return (
            self.__class__ is other.__class__ and
            self.as_dict() == other.as_dict()
        )

    def is_in_file_model(self):
        return self._filename_pattern(None) is not None

    @property
    def parent(self):
        return self._parent

    @parent.setter
    def parent(self, val):
        # Changing the parent of a involves too many changes which we avoid for
        # now, this may be revisited.
        if self._parent is not None:
            raise ModelParentAlreadySetError(self, 'parent already set')
        # The model must have a parent defined for it to accept it.
        parent_cfg = self._filename_pattern('parent')
        if parent_cfg is None:
            raise ModelNoParentDefinedError(self, 'no parent defined')
        # Which make sure that the type of the object given as a parent matches
        # with the type of the expected parent.
        if not isinstance(val, parent_cfg['class']):
            err = 'type {0} is not expected parent type {1}'
            err = err.format(type(val).__name__, parent_cfg['class'].__name__)
            raise ModelParentTypeError(self, err)
        # All good.
        self._parent = val

    def ref(self):
        """
        Model.ref returns a dictionary which can be used by ModelRef to
        reference this model from another model.
        """
        ref = {
            'clsname': model_name(self),
            'uuid': self.uuid,
        }
        ref.update(self._parents_refs_uuid())
        return ref

    def as_dict(self, session=None, owners=None):
        """
        This function returns the on-disk representation of this model. It is
        not safe to modify the value returned by this function in any way. This
        function is mostly internal and should be avoided.
        """
        if owners is None:
            owners = OwnerTracker()

        def _translate_to_raw_data(full_path, key, val):
            key_info = self._schema().key_info.get(full_path)
            if key_info is None:
                return val
            if key == 'category':
                print(key, val)
            type_ = key_info.T
            if is_model(type_):
                return val.as_dict(session=session, owners=owners)
            elif isinstance(type_, list) and is_model(type_[0]):
                return [v.as_dict(session=session, owners=owners) for v in val]
            elif is_custom_type(type_) and val is not None:
                return type_.dump(session, owners, val)
            elif isinstance(type_, list) and is_custom_type(type_[0]):
                return [type_[0].dump(session, owners, v) for v in val]
            return val

        with owners.wrap(self):
            tmp = _dict_utils.map(self._data, _translate_to_raw_data)

        tmp = _dict_utils.clear(tmp) or {}

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

    def filenames(self, owners=None):
        if owners is None:
            owners = OwnerTracker()

        result = []
        if self.is_in_file_model():
            result.append(self._model_filename())

        with owners.wrap(self):
            for key, key_info in self._schema().key_info.items():
                type_ = key_info.T

                if is_model(type_):
                    try:
                        val = _dict_utils.get_value(self._data, key.split('.'))
                        result.extend(val.filenames(owners=owners))
                    except KeyError:
                        pass

                if is_custom_type(type_):
                    try:
                        val = _dict_utils.get_value(self._data, key.split('.'))
                        result.extend(type_.filenames(owners, val))
                    except KeyError:
                        pass

                if isinstance(type_, list) and is_custom_type(type_[0]):
                    try:
                        vals = _dict_utils.get_value(self._data, key.split('.'))
                        for val in vals:
                            result.extend(type_[0].filenames(owners, val))
                    except KeyError:
                        pass

        return result

    def in_model_join(self, *args):
        dirname = os.path.dirname(self._model_filename())
        return os.path.join(self._session.rootdir, dirname, *args)

    @classmethod
    def _schema(cls):
        return cls.__lpbm_config__['schema']

    @classmethod
    def _filename_pattern(cls, item):
        filename_pattern = cls.__lpbm_config__.get('filename_pattern')
        if filename_pattern is None:
            return None
        if item is None:
            return filename_pattern
        return filename_pattern[item]
