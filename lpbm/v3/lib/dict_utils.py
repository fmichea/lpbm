def map(d, func, prefix=None):
    result = dict()
    for key, val in d.items():
        path = str(key)
        if prefix:
            path = '{0}.{1}'.format(prefix, path)
        val = func(path, key, val)
        if isinstance(val, dict):
            val = map(val, func, prefix=path)
        result[key] = val
    return result


def flatten(d, prefix=None):
    result = dict()
    for key, val in d.items():
        path = str(key)
        if prefix:
            path = '{0}.{1}'.format(prefix, path)
        if isinstance(val, dict):
            result.update(flatten(val, prefix=path))
        else:
            result[path] = val
    return result


def clear(d):
    result = dict()
    for key, val in d.items():
        if isinstance(val, dict):
            val = clear(val)
        if val is not None:
            result[key] = val
    return (result if result else None)


def get_value(data, keys):
    d = data
    for k in keys:
        d = d[k]
    return d


def set_value(data, keys, value):
    keys = keys[:]
    last_key = keys.pop()
    for k in keys:
        data = data.setdefault(k, {})
    data[last_key] = value


def delete_value(data, keys):
    # we are one past last key, nothing to do here.
    if not keys:
        return
    # get the key for this function and the remaining sub keys in the path.
    key, remaining_keys = keys[0], keys[1:]
    # if key is not in dict, the we do not delete anything.
    if key not in data:
        return
    # delete the value and all its possible parents.
    delete_value(data[key], remaining_keys)
    # If sub-dictionary is empty or we are on the last key, delete value.
    if not data[key] or not remaining_keys:
        del data[key]
