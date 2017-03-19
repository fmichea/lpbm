import pytest

import lpbm.v3.lib.dict_utils as mod


@pytest.fixture()
def d():
    return {'foo': {'bar': 1, 'blah': 123}, 'sisi': 6}


def test_map__first_param_is_full_path_to_val(d):
    def map_func(path, key, val):
        if isinstance(val, int):
            return path
        return val
    d2 = mod.map(d, map_func)
    assert d2['foo']['bar'] == 'foo.bar'
    assert d2['sisi'] == 'sisi'


def test_map__second_param_is_the_key(d):
    def map_func(path, key, val):
        if isinstance(val, int):
            return key
        return val
    d2 = mod.map(d, map_func)
    assert d2['foo']['bar'] == 'bar'
    assert d2['sisi'] == 'sisi'


def test_map__apply_func_recursively_to_dict(d):
    def map_func(path, key, val):
        if isinstance(val, int):
            return (val * 2 + 1)
        return val
    d2 = mod.map(d, map_func)
    assert d['sisi'] == 6 and d2['sisi'] == 13
    assert d['foo']['bar'] == 1 and d2['foo']['bar'] == 3


def test_flatten__returns_one_flat_directory(d):
    d2 = mod.flatten(d)
    assert d2['sisi'] == 6
    assert d2['foo.bar'] == 1
    assert d2['foo.blah'] == 123


def test_clear__removes_none_values_recursively(d):
    d.update({'foo2': {'va': True, 'kjnwed': {'wed': None}}, 'edj': None})
    d2 = mod.clear(d)
    assert d['edj'] is None
    assert 'edj' not in d2
    assert 'kjnwed' not in d2['foo2']


def test_get__test_recursive_get_no_error(d):
    assert mod.get_value(d, ['foo', 'bar']) == 1
    assert mod.get_value(d, ['sisi']) == 6


def test_get__test_key_not_found_error(d):
    with pytest.raises(KeyError):
        mod.get_value(d, ['wedwed'])


def test_set__test_recursive_and_simple_set(d):
    # setting existing values
    mod.set_value(d, ['sisi'], 12)
    assert d['sisi'] == 12
    mod.set_value(d, ['foo', 'blah'], 43)
    assert d['foo']['blah'] == 43
    # setting non-existing values
    mod.set_value(d, ['ahah'], 123545)
    assert d['ahah'] == 123545
    mod.set_value(d, ['foo', 'eheh', 'shoe'], 'eheh')
    assert d['foo']['eheh']['shoe'] == 'eheh'


def test_delete__test_simple_and_recursive_delete(d):
    # check the dictionary is as expected.
    assert 'sisi' in d
    assert 'foo' in d
    assert 'blah' in d['foo']
    assert 'bar' in d['foo']
    # deleting direct value is possible.
    mod.delete_value(d, ['sisi'])
    assert 'sisi' not in d
    # deleting recursive value is possibe
    mod.delete_value(d, ['foo', 'blah'])
    assert 'foo' in d
    assert 'blah' not in d['foo']
    # deleting recursive key that's only child deletes parent too.
    mod.delete_value(d, ['foo', 'bar'])
    assert 'foo' not in d
    # deleting unknown key is a noop.
    mod.delete_value(d, ['wedwed', 'erjf'])
