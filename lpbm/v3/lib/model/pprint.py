import json


def model_pformat(model):
    return json.dumps(model.as_dict(), indent=4, sort_keys=True)


def model_pprint(model, pfunc=print):
    pfunc(model_pformat(model))
