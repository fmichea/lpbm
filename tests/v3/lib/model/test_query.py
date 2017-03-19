import pytest

import lpbm.v3.lib.model as mod


@pytest.fixture
def a_model():
    class A(mod.Model):
        __lpbm_config__ = {
            'filename_pattern': 'as/{uuid}/a.yaml',
            'schema': {
                mod.Required('name'): str,
            },
        }

        name = mod.ModelField('name')

    return A


def test_query_for_all_with_no_objects_returns_empty_list(a_model, test_tempdir):
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = session.query(a_model).all()
        assert objects == []


def test_query_count_0_when_no_objects(a_model, test_tempdir):
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        assert session.query(a_model).count() == 0


def test_query_for_one_or_none_returns_none_when_no_objects(a_model, test_tempdir):
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        obj = session.query(a_model).one_or_none()
        assert obj is None


def test_query_for_first_or_none_returns_none_when_no_objects(a_model, test_tempdir):
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        obj = session.query(a_model).first_or_none()
        assert obj is None


@pytest.fixture
def objects_setup(a_model, test_tempdir):
    with mod.scoped_session_rw(rootdir=test_tempdir) as session:
        for name in ['foooo', 'blah', 'ehehe', 'whatup']:
            obj = a_model()
            obj.name = name
            session.add(obj)

    return a_model, test_tempdir


def test_query_load_all_objects_works(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = session.query(a_model).all()
        assert len(objects) == 4


@pytest.mark.parametrize('func,expected_len', [
    ((lambda x: x == 'foooo'), 1),
    ((lambda x: x == 'fooooooooo'), 0),
    ((lambda x: x != 'foooo'), 3),
    ((lambda x: x != 'fooooooooo'), 4),
])
def test_query_load_all_with_filters(func, expected_len, objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = session.query(a_model).filter(func(a_model.name)).all()
        assert len(objects) == expected_len
        assert all(func(obj.name) for obj in objects)


def test_query_ordering(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = session.query(a_model).order_by(a_model.name).all()
        assert len(objects) == 4
        assert objects[0].name == 'blah'
        assert objects[1].name == 'ehehe'
        assert objects[2].name == 'foooo'
        assert objects[3].name == 'whatup'


def test_query_ordering_and_filtering(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = (
            session.query(a_model)
                .order_by(a_model.name)
                .filter(a_model.name != 'foooo')
                .all()
        )
        assert len(objects) == 3
        assert objects[0].name == 'blah'
        assert objects[1].name == 'ehehe'
        assert objects[2].name == 'whatup'


def test_query_ordering_and_first_returns_right_val(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        obj = (
            session.query(a_model)
                .order_by(a_model.name)
                .filter(a_model.name != 'blah')
                .first()
        )
        assert obj is not None
        assert obj.name == 'ehehe'


def test_query_for_one_object_after_filtering(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        obj = session.query(a_model).filter(a_model.name == 'blah').one()
        assert obj is not None
        assert obj.name == 'blah'


def test_query_one_with_too_many_results_raises_exception(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryTooManyObjectsError):
            session.query(a_model).one()


def test_query_one_with_no_matches_raises_exception(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryNoObjectFoundError):
            session.query(a_model).filter(a_model.name == 'uh').one()


def test_query_first_with_no_matches_raises_exception(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryNoObjectFoundError):
            session.query(a_model).filter(a_model.name == 'uh').first()


def test_query_filter_criterion_must_be_modelfieldboolop(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryInvalidCriterionError):
            session.query(a_model).filter(234)


def test_query_order_by_criterion_must_be_model_field(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryInvalidCriterionError):
            session.query(a_model).order_by(1)


def test_query_can_delete_objects_directly_from_query(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_rw(rootdir=test_tempdir) as session:
        count = session.query(a_model).filter(a_model.name == 'blah').delete()
        assert count == 1

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        objects = session.query(a_model).all()
        assert len(objects) == 3


def test_query_get_for_direct_object_get(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        obj = session.query(a_model).filter(a_model.name == 'blah').one()
        obj2 = session.query(a_model).get(obj.uuid)
        assert obj == obj2
        assert obj is obj2


def test_query_get_an_unknown_uuid(objects_setup):
    a_model, test_tempdir = objects_setup

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryNoObjectFoundError):
            session.query(a_model).get('wedwed')


def test_cannot_use_parent_on_model_with_no_parent(a_model, test_tempdir):
    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mod.ModelQueryNoParentError):
            session.query(a_model).parent(None)


def test_query_parent_can_search_for_all_objects_or_parent(objects_setup):
    a_model, test_tempdir = objects_setup

    class B(mod.Model):
        __lpbm_config__ = {
            'schema': {
                mod.Required('value'): int,
            },
            'filename_pattern': a_model.inline_model('bs/{uuid}/b.yaml'),
        }

        value = mod.ModelField('value')

    with mod.scoped_session_rw(rootdir=test_tempdir) as session:
        a1 = session.query(a_model).filter(a_model.name == 'blah').first()

        b1 = B(parent=a1)
        b1.value = 123

        a2 = session.query(a_model).filter(a_model.name == 'whatup').first()

        b2 = B(parent=a2)
        b2.value = 1024

        session.add(b1, b2)

    with mod.scoped_session_ro(rootdir=test_tempdir) as session:
        bs = session.query(B).all()
        assert len(bs) == 2

        a = session.query(a_model).filter(a_model.name == 'blah').first()
        b = session.query(B).parent(a).one()
        assert b.value == 123

        # test cannot use parent twice.
        with pytest.raises(mod.ModelQueryParentAlreadySetError):
            session.query(B).parent(a).parent(a)

        # test cannot use the wrong type for parent.
        with pytest.raises(mod.ModelQueryParentWrongTypeError):
            session.query(B).parent(b)
