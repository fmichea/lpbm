class ModelFieldError(Exception):
    """
    ModelFieldError is the super-class of all errors raised when doing
    operations on a ModelField.
    """


class ModelFieldMissingError(ModelFieldError):
    """
    ModelFieldMissingError is raised when using getter on a field from a model
    with no value for that field in its data.
    """


class ModelFieldReadOnlyError(ModelFieldError):
    """
    ModelFieldReadOnlyError is raised when using setter on a field that is set
    to be read-only. The value of the field will not have been changed.
    """
