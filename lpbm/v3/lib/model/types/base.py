import abc


class BaseType(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def schema(self):
        pass

    @abc.abstractmethod
    def load(self, session, owner, value):
        pass

    @abc.abstractmethod
    def dump(self, session, owner, value):
        pass


def is_custom_type(val):
    return isinstance(val, BaseType)
