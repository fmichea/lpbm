import pytest

import lpbm.v3.lib.model as mod


def test_ref__needs_to_be_given_classes():
    with pytest.raises(mod.ModelRefInvalidDefinitionError):
        mod.ModelRef()


def test_ref__invalid_type_for_class_names():
    with pytest.raises(mod.ModelRefInvalidDefinitionError):
        mod.ModelRef(True)


def test_ref__invalid_deref():
    ref = mod.ModelRef('foo')
    with pytest.raises(mod.ModelRefInvalidClassError):
        ref.deref(None, {'clsname': 'bar'})


def test_ref__can_be_written_then_loaded(test_tempdir):
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
