import pytest

import lpbm.v3.lib.models as mod


def test_model__lpbm_config_required_for_model():
    with pytest.raises(TypeError) as exc:
        class A(mod.Model):
            pass

    assert str(exc.value) == 'model A must provide dict __lpbm_config__'


def test_model__lpbm_config_must_be_a_dictionary():
    with pytest.raises(TypeError) as exc:
        class A(mod.Model):
            __lpbm_config__ = None


    assert str(exc.value) == 'model A must provide dict __lpbm_config__'


def test_model__lpbm_config_without_schema_is_not_allowed():
    with pytest.raises(TypeError) as exc:
        class A(mod.Model):
            __lpbm_config__ = {}

    assert str(exc.value) == 'model A must provide a data schema in __lpbm_config__'


def test_model__test_simple_empty_model_no_field():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {},
        }

    a = A()
    assert a.as_dict() == {}


def test_model__test_simple_model_with_optional_field():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('foo'): str,
            },
        }

        foo = mod.ModelField('foo')

    assert isinstance(A.foo, mod.ModelField)

    a = A({})
    assert a.as_dict() == {}

    with pytest.raises(mod.ModelFieldMissingError):
        _ = a.foo

    a.foo = 'ahah'
    assert a.as_dict() == {'foo': 'ahah'}


def test_model__test_simple_with_default_value_for_field():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('foo', default='ahah'): str,
            },
        }

        foo = mod.ModelField('foo')

    a = A()
    assert a.foo == 'ahah'
    assert a.as_dict() == {'foo': 'ahah'}


def test_model__test_simple_model_with_required_field():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('foo'): str,
            },
        }

        foo = mod.ModelField('foo')

    a = A()
    with pytest.raises(mod.MultipleInvalid) as exc:
        a.as_dict()


def test_model__test_model_field_nested_struct_various_actions():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('foo'): {
                    mod.Optional('bar'): str,
                    mod.Optional('bal'): str,
                },
            },
        }

        foobar = mod.ModelField('foo.bar')
        foobal = mod.ModelField('foo.bal')

    a = A()
    assert a.as_dict() == {}

    a.foobar = 'wedwed'
    assert a.as_dict() == {'foo': {'bar': 'wedwed'}}
    assert a.foobar == 'wedwed'

    del a.foobar
    assert a.as_dict() == {}

    a.foobar = 'eheh'
    a.foobal = 'decombe'
    del a.foobar
    assert a.as_dict() == {'foo': {'bal': 'decombe'}}

    del a.foobar  # can delete an empty attribute.


def test_model__test_model_field_with_type_sub_model():
    class B(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('foo'): int,
                mod.Optional('baz', default=0): int,
            },
        }

        foo = mod.ModelField('foo')
        baz = mod.ModelField('baz')

    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('bar', default=B): B,
            },
        }

        bar = mod.ModelField('bar')

    a = A()
    assert a.as_dict() == {'bar': {'baz': 0}}

    a.bar.foo = 1
    assert a.as_dict() == {'bar': {'foo': 1, 'baz': 0}}

    a = A(a.as_dict())
    assert a.bar.foo == 1
    assert a.bar.baz == 0


def test_model__test_field_with_list():
    class B(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('foo'): int,
            },
        }

        foo = mod.ModelField('foo')

    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('bar', default=list): [B],
                mod.Optional('foo'): [int],
                mod.Optional('bal', default=list): [int],
            },
        }

        bar = mod.ModelField('bar')
        foo = mod.ModelField('foo')
        bal = mod.ModelField('bal')

    b = B()
    b.foo = 1

    a = A()
    a.bar.append(b)
    a.foo = [1, 2, 3, 4]

    assert a.as_dict() == {'bar': [{'foo': 1}], 'bal': [], 'foo': [1, 2, 3, 4]}
    assert a.bar[0].foo == 1

    d = a.as_dict()
    d.update({'bal': [int(c) for c in '1,2,3,4'.split(',')]})

    a = A(d)
    assert a.bar[0].foo == 1
    assert sum(a.foo) + sum(a.bal) == 20


def test_model__test_field_with_wrong_type_does_not_work():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': mod.Schema({
                mod.Required('foo'): int,
                mod.Required('bar'): int,
                'eheheheheheh': {
                    'oui': int,
                }
            }),
        }

        foo = mod.ModelField('foo')
        bar = mod.ModelField('bar')

    a = A({'foo': 'wedwed', 'bar': 1})
    assert a.bar == 1
    with pytest.raises(TypeError):
        a.foo


def test_model__test_save_and_load(monkeypatch, test_tempdir):
    monkeypatch.setattr(mod.lpath, '_EXEC_PATH', test_tempdir)

    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('name'): str,
            },
            'filename_pattern': 'as/{uuid}/state.yaml',
        }

        name = mod.ModelField('name')

    objects = A.load_all()
    assert not objects

    a = A()
    a.name = 'foooo'
    a.save()

    objects = A.load_all()
    assert len(objects) == 1

    a.delete()

    objects = A.load_all()
    assert not objects


def test_mode__test_model_equality_based_on_data():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                'name': str,
            },
        }

        name = mod.ModelField('name')

    a1, a2 = A(), A()
    assert a1 == a2

    a1.name = 'foo'
    assert a1 != a2

    a2.name = 'foo'
    assert a1 == a2
