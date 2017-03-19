from voluptuous import (
    Schema as _Schema,
    Required as _Required,
    ALLOW_EXTRA as _ALLOW_EXTRA,
)

from lpbm.v3.lib.model import data as lmdata
from lpbm.v3.lib.model.uuid import UUID as _UUID


MODEL_REF_SCHEMA = _Schema({
    _Required('clsname'): str,
    _Required('uuid'): _UUID,
}, extra=_ALLOW_EXTRA)


class ModelRef(object):
    def __init__(self, *clsnames):
        assert bool(clsnames)
        self._clsnames = set([
            clsname if isinstance(clsname, str) else clsname.__name__
            for clsname in clsnames
        ])

    def deref(self, session, val):
        clsname = val.pop('clsname')
        assert clsname in self._clsnames
        return session.query(lmdata.MODEL_NAME_TO_CLASS[clsname]).get(
            val['uuid'])


def is_model_ref(v):
    return isinstance(v, ModelRef)
