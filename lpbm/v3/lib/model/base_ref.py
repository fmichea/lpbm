from lpbm.v3.lib.model.base import model_name_id


class BaseModelRef(object):
    pass


def is_model_ref(v):
    return isinstance(v, BaseModelRef)


def model_ref_name_id(v):
    if isinstance(v, dict):
        return 'ModelRef(raw={raw})'.format(raw=v)
    if is_model_ref(v):
        clsnames = ','.join(v._clsnames)
        return 'ModelRef(definition={clsnames})'.format(clsnames=clsnames)
    return 'ModelRef(instance={ref})'.format(ref=model_name_id(v))
