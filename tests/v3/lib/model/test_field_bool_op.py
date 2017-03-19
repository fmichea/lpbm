import operator

import pytest

from lpbm.v3.lib.model import ModelField
from lpbm.v3.lib.model.errors import ModelFieldBoolOpError

import lpbm.v3.lib.model.field_bool_op as mod


class mock_model:
    def __init__(self, data):
        self.data = data


@pytest.fixture()
def fields(monkeypatch):
    def get(self, instance):
        return instance.data[int(self.path)]

    monkeypatch.setattr(ModelField, 'get', get)

    return [ModelField(str(x)) for x in range(3)]


@pytest.mark.parametrize('op,invals,outvals,res', [
    (operator.eq, [1, 2, 3], [1, 2, 3], True),
    (operator.eq, [2, 2, 3], [1, 2, 3], False),
    (operator.eq, [1, 3, 3], [1, 2, 3], False),
    (operator.eq, [1, 2, 4], [1, 2, 3], False),

    (operator.ne, [1, 2, 3], [1, 2, 3], False),
    (operator.ne, [2, 2, 3], [1, 2, 3], False),
    (operator.ne, [4, 3, 3], [1, 2, 3], False),
    (operator.ne, [3, 9, 4], [1, 2, 3], True),
])
def test_and__true_only_if_all_are_true(op, invals, outvals, res, fields):
    tests = [op(field, outvals[idx]) for idx, field in enumerate(fields)]
    assert mod.and_(*tests).test(mock_model(invals)) is res


def test_and__does_not_accept_non_bool_op():
    with pytest.raises(ModelFieldBoolOpError):
        mod.and_(object())


@pytest.mark.parametrize('op,invals,outvals,res', [
    (operator.eq, [1, 2, 3], [1, 2, 3], True),
    (operator.eq, [2, 2, 3], [1, 2, 3], True),
    (operator.eq, [5, 3, 3], [1, 2, 3], True),
    (operator.eq, [0, 8, 4], [1, 2, 3], False),

    (operator.ne, [1, 2, 3], [1, 2, 3], False),
    (operator.ne, [2, 2, 3], [1, 2, 3], True),
    (operator.ne, [4, 3, 3], [1, 2, 3], True),
    (operator.ne, [3, 9, 4], [1, 2, 3], True),
])
def test_or__true_when_any_true(op, invals, outvals, res, fields):
    tests = [op(field, outvals[idx]) for idx, field in enumerate(fields)]
    assert mod.or_(*tests).test(mock_model(invals)) is res


def test_or__does_not_accept_non_bool_op():
    with pytest.raises(ModelFieldBoolOpError):
        mod.or_(object())


@pytest.mark.parametrize('invals,res', [
    ((1, 2, 3), True),
    ((1, 5, 3), True),
    ((5, 5, 3), True),

    ((5, 2, 3), False),
    ((1, 2, 4), False),
])
def test_combination__advanced_test(invals, res, fields):
    t = mod.and_(mod.or_(fields[0] == 1, fields[1] != 2), fields[2] == 3)
    assert t.test(mock_model(invals)) is res
