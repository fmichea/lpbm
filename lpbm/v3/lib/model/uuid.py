import re

from lpbm.v3.lib.uuid import new_uuid

UUID_RE_S = '[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}'
UUID_RE = re.compile('^{uuid_re}$'.format(uuid_re=UUID_RE_S))


def UUID(val):
    if not isinstance(val, str):
        raise ValueError('uuid must be a string')
    if UUID_RE.match(val) is None:
        raise ValueError('invalid uuid format {val!r}'.format(val=val))
    return val
