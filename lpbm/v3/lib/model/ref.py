from voluptuous import ALLOW_EXTRA as _ALLOW_EXTRA
from voluptuous import Required as _Required
from voluptuous import Schema as _Schema

from lpbm.v3.lib.model import data
from lpbm.v3.lib.model.base import (
    is_model,
    model_name,
    model_name_id,
)
from lpbm.v3.lib.model.base_ref import (
    BaseModelRef,
    is_model_ref,
    model_ref_name_id,
)
from lpbm.v3.lib.model.errors import (
    ModelRefDefinitionError,
    ModelRefInvalidClassError,
    ModelRefNoSessionError,
    ModelRefNotInSessionError,
)
from lpbm.v3.lib.model.uuid import UUID as _UUID

MODEL_REF_SCHEMA = _Schema({
    _Required('clsname'): str,
    _Required('uuid'): _UUID,
}, extra=_ALLOW_EXTRA)


class ModelRef(BaseModelRef):
    def __init__(self, *clsnames):
        if not clsnames:
            raise ModelRefDefinitionError('no class names provided')

        self._clsnames = set()
        for clsname in clsnames:
            if is_model(clsname):
                clsname = model_name(clsname)
            if not isinstance(clsname, str):
                err = 'expected string or model, but got {0!r}'
                raise ModelRefDefinitionError(err.format(clsname))
            self._clsnames.add(clsname)

    def ref(self, session, owner, val):
        if session is None:
            raise ModelRefNoSessionError(owner, val)

        if not session.is_in(val):
            raise ModelRefNotInSessionError(owner, val)

        ref = val.ref()

        clsname = ref.get('clsname')
        if clsname not in self._clsnames:
            raise ModelRefInvalidClassError(owner, val, clsname, self._clsnames)

        return ref

    def deref(self, session, owner, val):
        if session is None:
            raise ModelRefNoSessionError(owner, val)

        clsname = val.get('clsname')
        if clsname not in self._clsnames:
            raise ModelRefInvalidClassError(owner, val, clsname, self._clsnames)

        return session.query(data.MODEL_NAME_TO_CLASS[clsname]).get(**val)
