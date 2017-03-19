import abc

from lpbm.v3.lib.model.errors import ModelFieldBoolOpError


class ModelFieldBoolOp(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def test(self, instance):
        """
        This function tests model field boolean expression on a specific
        instance. There are three types of tests currently: and expression, or
        expression and one parameter boolean tests.
        """


class ModelFieldTest(ModelFieldBoolOp):
    def __init__(self, op, model_field, value):
        self._op = op
        self._model_field = model_field
        self._value = value

    def test(self, instance):
        return self._op(self._model_field.get(instance), self._value)


class and_(ModelFieldBoolOp):
    def __init__(self, *ops):
        for op in ops:
            if not isinstance(op, ModelFieldBoolOp):
                raise ModelFieldBoolOpError('and_ expects bool op')
        self._ops = ops

    def test(self, instance):
        return all(op.test(instance) for op in self._ops)


class or_(ModelFieldBoolOp):
    def __init__(self, *ops):
        for op in ops:
            if not isinstance(op, ModelFieldBoolOp):
                raise ModelFieldBoolOpError('or_ expects bool op')
        self._ops = ops

    def test(self, instance):
        return any(op.test(instance) for op in self._ops)
