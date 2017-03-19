import lpbm.v3.lib.model.base as mod


def test_model__test_main_model_or_inherited():
    class B(mod.BaseModel):
        pass

    assert not mod.is_model(int)
    assert mod.is_model(mod.BaseModel)
    assert mod.is_model(B)


def test_model__test_instances():
    class B(mod.BaseModel):
        pass

    assert not mod.is_model_instance(object())
    assert mod.is_model_instance(mod.BaseModel())
    assert mod.is_model_instance(B())
