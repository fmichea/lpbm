class BaseModel(object):
    pass


def is_model(v):
    return isinstance(v, type) and issubclass(v, BaseModel)


def is_model_instance(v):
    return isinstance(v, BaseModel)


def model_name(v):
    if v is None:
        return 'None'
    if is_model_instance(v):
        return model_name(v.__class__)
    return v.__name__


def model_name_id(v):
    res = model_name(v)
    if v.is_in_file_model():
        res += '(uuid={uuid})'.format(uuid=v.uuid)
    return res
