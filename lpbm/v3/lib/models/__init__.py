import inspect
import os
import uuid
import yaml

import lpbm.v3.lib.path as lpath

from voluptuous import (
    Schema as _Schema,
    Marker as _Marker,
    Required,
    Optional,
    Email,
    Boolean,
    Any,
    UNDEFINED as _UNDEFINED,
)
from voluptuous.error import MultipleInvalid


def _new_uuid():
    return str(uuid.uuid4())


_NOT_SET = object()


class _BaseModel(object):
    pass


def is_model(v):
    return isinstance(v, type) and issubclass(v, _BaseModel)


def is_model_instance(v):
    return isinstance(v, _BaseModel)


def _build_real_schema(schema):
    if is_model(schema):
        return schema._schema()
    if isinstance(schema, dict):
        return {
            key: _build_real_schema(val)
            for key, val in schema.items()
        }
    if isinstance(schema, list):
        assert len(schema) == 1
        return [_build_real_schema(schema[0])]
    return schema


def _build_marker_index(d, prefix=None):
    markers, types = dict(), dict()
    for key, val in d.items():
        path = str(key)
        if prefix:
            path = '{0}.{1}'.format(prefix, path)
        # markers.
        if isinstance(key, _Marker):
            markers[path] = key
        # types.
        if isinstance(val, dict):
            tmp1, tmp2 = _build_marker_index(val, prefix=path)
            markers.update(tmp1)
            types.update(tmp2)
        elif is_model(val):
            types[path] = val
        elif isinstance(val, list) and is_model(val[0]):
            types[path] = val
        elif any(val is t for t in (bool, int, float, str)):
            types[path] = val
    return markers, types


class Schema(_Schema):
    def __init__(self, schema, **kw):
        super().__init__(_build_real_schema(schema), **kw)
        self.model_schema = schema
        # For ModelField we need to have easy access to the Markers.
        self.markers, self.types = _build_marker_index(self.model_schema)

    def extend(self, other):
        self.schema = super(Schema, self).extend(_build_real_schema(other)).schema
        self._compiled = self._compile(self.schema)

        self.model_schema.update(other)

        tmp1, tmp2 = _build_marker_index(other)
        self.markers.update(tmp1)
        self.types.update(tmp2)


class ModelFieldMissingError(Exception):
    pass


class ModelField(object):
    def __init__(self, path):
        self.path, self.path_sp = path, path.split('.')

    def __get__(self, instance, type=None):
        if instance is None:
            return self

        marker = instance._schema().markers.get(self.path)
        types = instance._schema().types.get(self.path)

        prev_d = d = instance._data
        try:
            for k in self.path_sp:
                prev_d = d
                d = d[k]
            if types is not None:
                if is_model(types) and isinstance(d, dict):
                    d = types(data=d)
                elif isinstance(types, list) and is_model(types[0]):
                    d = [x if is_model_instance(x) else types[0](x) for x in d]
                elif types is not None and not isinstance(d, types):
                    raise TypeError('invalid type for model field')
            prev_d[k] = d
        except KeyError:
            if marker is None or marker.default is _UNDEFINED:
                msg = 'field not found {0}'.format(self.path)
                raise ModelFieldMissingError(msg)
            d = marker.default()
            self.__set__(instance, d)
        return d

    def __set__(self, instance, value):
        data = instance._data
        keys = self.path.split('.')
        last_key = keys.pop()
        for k in keys:
            data = data.setdefault(k, {})
        data[last_key] = value

    def __delete__(self, instance):
        def delete_key_from_dict(d, path):
            # for last key, we get None as path.
            if path is None:
                return
            # split on first dot of path.
            try:
                key, subpath = path.split('.', 1)
            except ValueError:
                key, subpath = path, None
            # if key is not in dict, then we do not have anything to delete.
            if key not in d:
                return
            # delete subpath from sub-directory.
            delete_key_from_dict(d[key], subpath)
            # if sub-directory is empty or we are on last key, delete value.
            if not d[key] or subpath is None:
                del d[key]

        delete_key_from_dict(instance._data, self.path)


class _ModelMeta(type):
    def __new__(cls, name, bases, namespace, **kw):
        kw = dict(namespace)

        if '__lpbm_config__' not in kw or not isinstance(kw['__lpbm_config__'], dict):
            err = 'model {class_name} must provide dict __lpbm_config__'
            raise TypeError(err.format(class_name=name))

        if 'schema' not in kw['__lpbm_config__']:
            err = 'model {class_name} must provide a data schema in __lpbm_config__'
            raise TypeError(err.format(class_name=name))

        schema = kw['__lpbm_config__']['schema']
        if schema is not None:
            if isinstance(schema, dict):
                schema = Schema(schema)
            if 'filename_pattern' in kw['__lpbm_config__']:
                schema.extend({
                    Required('uuid', default=_new_uuid): str,
                })
                kw['uuid'] = ModelField('uuid')
            kw['__lpbm_config__']['schema'] = schema

        return super().__new__(cls, name, bases, kw)


class Model(_BaseModel, metaclass=_ModelMeta):
    __lpbm_config__ = {
        'schema': None,
        'filename_pattern': None,
    }

    def __init__(self, data=None):
        if data is None:
            data = dict()
        self._data = data

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self.as_dict() == other.as_dict()
        )

    def as_dict(self):
        def _simple_value(val):
            if isinstance(val, Model):
                return val.as_dict()
            if isinstance(val, dict):
                return {k: _simple_value(v) for k, v in val.items()}
            if isinstance(val, list):
                return [_simple_value(v) for v in val]
            return val
        # We save the data to the model so generated values are kept.
        self._data = _simple_value(self._schema()(_simple_value(self._data)))
        return self._data

    def save(self):
        contents = yaml.safe_dump(self.as_dict(), default_flow_style=False)
        filename = self.__lpbm_config__['filename_pattern'].format(uuid=self.uuid)

        path = lpath.in_blog_join(filename)
        broot = os.path.dirname(path)
        lpath.mkdir_p(broot)

        with open(path, 'w') as fd:
            fd.write(contents)

    def delete(self):
        filename = self.__lpbm_config__['filename_pattern'].format(uuid=self.uuid)
        lpath.remove(lpath.in_blog_join(filename))

    @classmethod
    def load_all(cls):
        parts = lpath.full_split(cls.__lpbm_config__['filename_pattern'])

        root, part = '', parts.pop()
        while part != '{uuid}':
            root = os.path.join(root, part)
            part = parts.pop()

        assert len(parts) == 1

        result = []

        broot = lpath.in_blog_join(root)

        if os.path.exists(broot):
            for uuid in os.listdir(broot):
                filename = os.path.join(broot, uuid, *parts)
                if not os.path.exists(filename):
                    continue
                result.append(cls.load_from_file(uuid, filename))
        return result

    @classmethod
    def load_from_file(cls, uuid, filename):
        with open(filename) as fd:
            data = yaml.safe_load(fd.read())
        return cls(cls._schema()(data))

    @classmethod
    def _schema(cls):
        return cls.__lpbm_config__['schema']
