from collections import namedtuple

from voluptuous import UNDEFINED as _UNDEFINED
from voluptuous import Marker as _Marker
from voluptuous import Schema as _Schema

from lpbm.v3.lib import dict_utils as _dict_utils
from lpbm.v3.lib.model.base import is_model
from lpbm.v3.lib.model.types.base import is_custom_type


def _build_real_schema(d):
    def _extract_real_schema_data(full_path, key, val):
        if is_model(val):
            return val._schema()
        if is_custom_type(val):
            return val.schema()
        if isinstance(val, list):
            assert len(val) == 1
            return [_extract_real_schema_data(None, None, val[0])]
        return val
    return _dict_utils.map(d, _extract_real_schema_data)


_ModelKeyInfo = namedtuple('_ModelKeyInfo', ['marker', 'T'])


def _build_key_info(d):
    def _extract_key_info(full_path, key, val):
        if (
            is_model(val) or
            is_custom_type(val) or
            (isinstance(val, list) and is_model(val[0])) or
            (isinstance(val, list) and is_custom_type(val[0])) or
            any(val is t for t in (bool, int, float, str))
        ):
            return _ModelKeyInfo(marker=key, T=val)

    tmp = _dict_utils.map(d, _extract_key_info)
    return _dict_utils.clear(_dict_utils.flatten(tmp)) or {}


def _build_data_defaults(d):
    def _extract_default_funcs(full_path, key, val):
        if isinstance(key, _Marker) and key.default is not _UNDEFINED:
            return key.default

    tmp = _dict_utils.map(d, _extract_default_funcs)
    return _dict_utils.flatten(_dict_utils.clear(tmp) or {})


class ModelSchema(_Schema):
    def __init__(self, schema, **kw):
        super().__init__(_build_real_schema(schema), **kw)
        # For ModelField we need to have easy access to the Markers and types.
        self.model_schema = schema

        self.key_info = _build_key_info(self.model_schema)
        self.data_defaults = _build_data_defaults(self.model_schema)
