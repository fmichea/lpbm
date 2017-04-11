import pytest

import lpbm.v3.lib.model as mod


def test_ref__needs_to_be_given_classes():
    with pytest.raises(mod.ModelRefDefinitionError) as exc:
        mod.ModelRef()

    assert str(exc.value) == 'no class names provided'


def test_ref__invalid_type_for_class_names():
    with pytest.raises(mod.ModelRefDefinitionError) as exc:
        mod.ModelRef(True)

    assert str(exc.value) == 'expected string or model, but got True'


def test_ref__invalid_ref_and_deref(test_tempdir):
    ref = mod.ModelRef('foo')

    assert mod.model_ref_name_id(ref) == 'ModelRef(definition=foo)'

    class fooo:
        __name__ = 'fooo'

    with pytest.raises(mod.ModelRefNoSessionError) as exc:
        ref.deref(None, fooo(), {})

    with pytest.raises(mod.ModelRefNoSessionError) as exc:
        ref.ref(None, fooo(), {})

    assert str(exc.value).endswith('no session provided when (de)referencing')

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelRefInvalidClassError) as exc:
            ref.deref(session, fooo(), {'clsname': 'fooo'})

        exc_str = str(exc.value)
        assert exc_str.endswith('object of type "fooo" is not in "foo"')


@pytest.fixture()
def ab_klasses():
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

    return A, B


def test_ref__can_be_written_then_loaded(ab_klasses, test_tempdir):
    A, B = ab_klasses

    with mod.scoped_session_rw(rootdir=test_tempdir) as session:
        a = A()
        a.name = 'wedwed'

        a_uuid = a.uuid

        b = B()
        b.name = 'foo'
        b.a_main_ref = a

        session.add(a, b)

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        b = session.query(B).one()
        assert isinstance(b.a_main_ref, A)
        assert b.a_main_ref.uuid == a_uuid


@pytest.mark.parametrize('setter', [
    (lambda b, a: setattr(b, 'a_main_ref', a)),
    (lambda b, a: setattr(b, 'a_refs', [a])),
])
def test_ref__test_ref_to_unknown_object_not_accepted(ab_klasses, setter, test_tempdir):
    A, B = ab_klasses

    with pytest.raises(mod.ModelRefNotInSessionError) as exc:
        with mod.scoped_session_rw(rootdir=test_tempdir) as session:
            a = A()
            a.name = 'bloupbloup'

            b = B()
            b.name = 'blah'
            setter(b, a)

            session.add(b)

    exc_str = str(exc.value)
    assert 'object referenced is not in session' in exc_str


def test_ref__cannot_use_wrong_type(ab_klasses, test_tempdir):
    A, B = ab_klasses

    with pytest.raises(mod.ModelRefInvalidClassError) as exc:
        with mod.scoped_session_rw(rootdir=test_tempdir) as session:
            b = B()
            b.name = 'blah'
            b.a_main_ref = b

            session.add(b)

    exc_str = str(exc.value)
    assert exc_str.endswith('object of type "B" is not in "A"')
