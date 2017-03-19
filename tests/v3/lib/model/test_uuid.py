import pytest

import lpbm.v3.lib.model.uuid as mod


def test_new_uuid__returns_uuid_string():
    uuid = mod.new_uuid()
    assert isinstance(uuid, str)
    assert mod.UUID(uuid) == uuid


@pytest.mark.parametrize('val,excstr', [
    (None, 'uuid must be a string'),
    (234, 'uuid must be a string'),

    ('wed', 'invalid uuid format \'wed\''),
    ('123', 'invalid uuid format \'123\''),
])
def test_UUID__test_all_failure_cases(val, excstr):
    with pytest.raises(ValueError) as exc:
        mod.UUID(val)
    assert str(exc.value) == excstr
