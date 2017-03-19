import pytest

import lpbm.v3.lib.model as mod
import lpbm.v3.lib.path as lpath


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


def test_model__test_schema_must_be_dict():
    with pytest.raises(TypeError) as exc:
        class A(mod.Model):
            __lpbm_config__ = {
                'schema': 1,
            }

    assert str(exc.value) == 'model A must provide data schema as a dict'


def test_model__test_simple_empty_model_no_field():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {},
        }

    a = A()
    assert mod.is_model_instance(a)
    assert a.as_dict() == {}
    assert repr(a)


def test_model__test_no_two_classes_with_same_name():
    class A(mod.Model):
        __lpbm_config__ = {'schema': {}}

    with pytest.raises(TypeError) as exc:
        class A(mod.Model):
            __lpbm_config__ = {'schema': {}}

    assert str(exc.value) == 'Invalid model name A used for two models'


@pytest.fixture()
def a_model():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('name'): str,
            },
        }

        name = mod.ModelField('name')

    return A


def test_model__test_model_field_no_instance_returns_the_field(a_model):
    assert isinstance(a_model.name, mod.ModelField)


def test_model__test_simple_model_with_optional_field_empty_dict(a_model):
    a = a_model({})
    assert a.as_dict() == {}


def test_model__field_not_set_return_missing_error(a_model):
    a = a_model({})
    with pytest.raises(mod.ModelFieldMissingError):
        _ = a.name


def test_model__setting_field_adds_value_to_as_dict(a_model):
    a = a_model({})
    a.name = 'ahah'
    assert a.as_dict() == {'name': 'ahah'}


def test_model__test_simple_with_default_value_for_field_and_read_only():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('foo', default='ahah'): str,
            },
        }

        foo = mod.ModelField('foo', read_only=True)

    a = A()
    assert a.foo == 'ahah'
    assert a.as_dict() == {'foo': 'ahah'}

    with pytest.raises(mod.ModelFieldReadOnlyError):
        a.foo = 'wdewde'


def test_model__test_simple_model_with_required_field():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('foo'): str,
            },
        }

        foo = mod.ModelField('foo')

    a = A()
    with pytest.raises(mod.ModelInvalidError) as exc:
        a.as_dict()

    exc_str = str(exc.value)
    assert exc_str.startswith('A:')
    assert 'required' in exc_str
    assert '\'foo\'' in exc_str

    class B(mod.Model):
        __lpbm_config__ = {
            'filename_pattern': '{uuid}/foo.yaml',
            'schema': {
                mod.Required('foo'): str,
            },
        }

        foo = mod.ModelField('foo')

    b = B()
    with pytest.raises(mod.ModelInvalidError) as exc:
        b.as_dict()

    exc_str = str(exc.value)
    assert exc_str.startswith('B uuid={0}:'.format(b.uuid))


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


def test_model__test_field_with_list(a_model):
    class B(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Optional('bar', default=list): [a_model],
                mod.Optional('foo'): [int],
                mod.Optional('bal', default=list): [int],
            },
        }

        bar = mod.ModelField('bar')
        foo = mod.ModelField('foo')
        bal = mod.ModelField('bal')

    a = a_model()
    a.name = 'oh'

    b = B()
    b.bar.append(a)
    b.foo = [1, 2, 3, 4]

    assert b.as_dict() == {'bar': [{'name': 'oh'}], 'bal': [], 'foo': [1, 2, 3, 4]}
    assert b.bar[0].name == 'oh'

    d = b.as_dict()
    d.update({'bal': [int(c) for c in '1,2,3,4'.split(',')]})

    b = B(d)
    assert b.bar[0].name == 'oh'
    assert sum(b.foo) + sum(b.bal) == 20


def test_model__test_field_with_wrong_type_does_not_work():
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('foo'): int,
                mod.Required('bar'): int,
                'eheheheheheh': {
                    'oui': int,
                }
            },
        }

        foo = mod.ModelField('foo')
        bar = mod.ModelField('bar')

    with pytest.raises(mod.ModelInvalidError):
        a = A({'foo': 'wedwed', 'bar': 1})


def test_model__test_save_and_load(monkeypatch, test_tempdir):
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('name'): str,
            },
            'filename_pattern': 'as/{uuid}/state.yaml',
        }

        name = mod.ModelField('name')

    class B(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('label'): str,
            },
            'filename_pattern': A.inline_model('bs/{uuid}/this.yaml'),
        }

        label = mod.ModelField('label')

    with mod.scoped_session_rw(rootdir=test_tempdir) as session:
        objects = session.query(A).all()
        assert not objects

        a = A()
        a.name = 'foooo'
        assert a.uuid in repr(a)

        a_uuid = a.uuid
        a_dict = a.as_dict()

        session.add(a)

    # Check that all() returns the same object than a.
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = session.query(A).all()
        assert len(objects) == 1
        assert objects[0].as_dict() == a_dict

    # Check that we can load with a direct get.
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        a = session.query(A).get(a_uuid)
        assert a is not None
        assert a.as_dict() == a_dict


def test_model__test_model_equality_based_on_data():
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


def test_model__test_model_reference(monkeypatch, test_tempdir):
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                'name': str,
            },
            'filename_pattern': 'as/{uuid}/a.yaml',
        }

        name = mod.ModelField('name')

    class B(mod.Model):
        __lpbm_config__ = {
            'schema': {
                'name': str,
                mod.Optional('a_main_ref', default=A): mod.ModelRef(A),
                mod.Optional('a_refs', default=list): [mod.ModelRef(A)],
            },
            'filename_pattern': 'bs/{uuid}/b.yaml',
        }

        name = mod.ModelField('name')
        a_main_ref = mod.ModelField('a_main_ref')
        a_refs = mod.ModelField('a_refs')

    with mod.scoped_session_rw(rootdir=test_tempdir) as session:
        a = A()
        a.name = 'fooooo'

        b = B()
        b.name = 'bar'
        b.a_main_ref = a
        b.a_refs.append(a)

        session.add(a, b)


def test_model__pformat_and_pprint(capsys):
    class A(mod.Model):
        __lpbm_config__ = {
            'schema': {
                'name': str,
                'full_name': str,
            },
        }

        name = mod.ModelField('name')
        full_name = mod.ModelField('full_name')

    a = A()
    a.name = 'foo'

    assert mod.model_pformat(a) == '{\n    "name": "foo"\n}'

    a.full_name = 'Foo Bar'

    val = '{\n    "full_name": "Foo Bar",\n    "name": "foo"\n}'
    assert mod.model_pformat(a) == val

    capsys.readouterr()
    mod.model_pprint(a)
    out, _ = capsys.readouterr()
    assert out == (val + '\n')
