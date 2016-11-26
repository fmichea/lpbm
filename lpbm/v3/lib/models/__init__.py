import inspect
import os
import uuid

import yaml

import lpbm.v3.lib.path as lpath


_NOT_SET = object()


class _BaseModel(object):
    pass


class ModelField(object):
    def __init__(self, path, **kw):
        self.path = path
        self._type = kw.get('type', None)
        self._value_type = kw.get('value_type', None)
        if self._type is list:
            assert self._value_type != None
        # Default value can be a constant or a function that will be called.
        self._default = kw.get('default', _NOT_SET)

    def has_default(self):
        return self._default is not _NOT_SET

    def default(self):
        if inspect.isfunction(self._default):
            return self._default()
        return self._default

    def _type_cast(self, val):
        if issubclass(self._type, _BaseModel):
            return self._type.new(val)
        if not isinstance(val, self._type):
            raise
        return val

    def _value_type_cast(self, val):
        if self._value_type is None:
            return val
        if isinstance(val, self._value_type):
            return val
        if issubclass(self._value_type, _BaseModel):
            return self._value_type.new(val)
        return self._value_type(val)

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        prev_d = d = instance.data
        try:
            for k in self.path.split('.'):
                prev_d = d
                d = d[k]
            if self._type is not None:
                d = self._type_cast(d)
            if isinstance(d, list):
                d = [self._value_type_cast(d1) for d1 in d]
                prev_d[k] = d
        except Exception as exc:
            if not self.has_default():
                raise
            d = self.default()
            self.__set__(instance, d)
        return d

    def __set__(self, instance, value):
        data = instance.data
        keys = self.path.split('.')
        last_key = keys.pop()
        for k in keys:
            data = data.setdefault(k, {})
        data[last_key] = value

    def __delete__(self):
        pass


class _ModelMeta(type):
    def __new__(cls, name, bases, namespace, **kw):
        kw = dict(namespace)

        if '__lpbm_config__' not in kw:
            raise Exception('shit')

        if 'schema' not in kw['__lpbm_config__']:
            raise Exception('shit2')

        return super().__new__(cls, name, bases, namespace)


class Model(_BaseModel, metaclass=_ModelMeta):
    __lpbm_config__ = {
        'schema': None,
        'filename_pattern': None,
    }

    def __init__(self, uuid, data):
        self.uuid, self.data = uuid, data

    def __eq__(self, other):
        return (
            self.__class__ is other.__class__ and
            self.data == other.data
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
        return self.__schema(_simple_value(self.data))

    def save(self):
        contents = yaml.safe_dump(self.as_dict(), default_flow_style=False)
        filename = self.__lpbm_config__['filename_pattern'].format(uuid=self.uuid)

        path = lpath.in_blog_join(filename)
        broot = os.path.dirname(path)
        import lpbm.tools as ltools; ltools.mkdir_p(broot)

        with open(path, 'w') as fd:
            fd.write(contents)

    def delete(self):
        filename = self.__lpbm_config__['filename_pattern'].format(uuid=self.uuid)
        path = lpath.in_blog_join(filename)
        import os; os.remove(path)

    @classmethod
    def load_all(cls):
        def full_split(path):
            parts, head = [], None
            while head != '':
                head, tail = os.path.split(path)
                parts.append(tail)
                path = head
            return parts

        parts = full_split(cls.__lpbm_config__['filename_pattern'])

        root = parts.pop()
        while True:
            part = parts.pop()
            if part == '{uuid}':
                break
            root = os.path.join(root, part)

        assert len(parts) == 1

        result = []

        broot = lpath.in_blog_join(root)

        if os.path.exists(broot):
            for uuid in os.listdir(broot):
                filename = os.path.join(root, uuid, parts[0])
                if not os.path.exists(filename):
                    continue
                result.append(cls.load_from_file(uuid, filename))
        return result

    @classmethod
    def new(cls, data=None):
        if data is None:
            data = {}
        return cls(str(uuid.uuid4()), data)

    @classmethod
    def load_from_file(cls, uuid, filename):
        with open(filename) as fd:
            data = yaml.safe_load(fd.read())
        return cls(uuid, cls.__schema(data))

    @classmethod
    def __schema(cls, data):
        return cls.__lpbm_config__['schema'](data)
