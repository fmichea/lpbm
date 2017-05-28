import abc


class BaseType(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def schema(self):
        """
        BaseType.schema returns the schema for this type.
        """

    def filenames(self, owners, value):
        return []

    @abc.abstractmethod
    def load(self, session, owners, value):
        """
        BaseType.load takes raw data and returns values from that data.
        """

    @abc.abstractmethod
    def dump(self, session, owners, value):
        """
        BaseType.dump takes data and translates it to raw data so it can be
        dumped to files.
        """


def is_custom_type(val):
    return isinstance(val, BaseType)
