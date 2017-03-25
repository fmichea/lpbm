class BaseModel(object):
    pass


def is_model(v):
    return isinstance(v, type) and issubclass(v, BaseModel)


def is_model_instance(v):
    return isinstance(v, BaseModel)


def model_name(v):
    if is_model_instance(v):
        return model_name(v.__class__)
    return v.__name__
