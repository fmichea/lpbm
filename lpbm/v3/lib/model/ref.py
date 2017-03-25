from voluptuous import (
    Schema as _Schema,
    Required as _Required,
    ALLOW_EXTRA as _ALLOW_EXTRA,
)

from lpbm.v3.lib.model import data
from lpbm.v3.lib.model.base import (
    is_model,
    model_name,
)
from lpbm.v3.lib.model.errors import (
    ModelRefInvalidClassError,
    ModelRefInvalidDefinitionError,
)
from lpbm.v3.lib.model.uuid import UUID as _UUID


MODEL_REF_SCHEMA = _Schema({
    _Required('clsname'): str,
    _Required('uuid'): _UUID,
}, extra=_ALLOW_EXTRA)


class ModelRef(object):
    def __init__(self, *clsnames):
        if not clsnames:
            raise ModelRefInvalidDefinitionError('no class names provided')

        self._clsnames = set()
        for clsname in clsnames:
            if is_model(clsname):
                clsname = model_name(clsname)
            if not isinstance(clsname, str):
                err = 'expected string or model but got {0!r}'
                raise ModelRefInvalidDefinitionError(err.format(clsname))
            self._clsnames.add(clsname)

    def deref(self, session, val):
        clsname = val.pop('clsname')
        if clsname not in self._clsnames:
            raise ModelRefInvalidClassError()
        return session.query(data.MODEL_NAME_TO_CLASS[clsname]).get(**val)


def is_model_ref(v):
    return isinstance(v, ModelRef)
