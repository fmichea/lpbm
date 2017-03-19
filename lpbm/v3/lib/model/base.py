class BaseModel(object):
    pass


def is_model(v):
    return isinstance(v, type) and issubclass(v, BaseModel)


def is_model_instance(v):
    return isinstance(v, BaseModel)
