from lpbm.v3.lib.model.base import model_name
from lpbm.v3.lib.model.base_ref import model_name_id


class ModelError(Exception):
    """
    ModelError is the super-class of all Model exceptions.
    """

    def __init__(self, model, fmt, **kw):
        self._model = model
        self._err = fmt.format(**kw)

    def __str__(self):
        return '{0}: {1}'.format(model_name_id(self._model), self._err)


class ModelInvalidError(ModelError):
    """
    ModelInvalidError is raised when verify-ing model data based on contents.
    """


class ModelParentError(ModelError):
    """
    ModelParentError is a super-class of all exceptions raised when errors
    happen with parents of inline models
    """


class ModelParentAlreadySetError(ModelParentError):
    """
    ModelParentAlreadySetError is raised when an attempt is made to change the
    parent of an inline model that already has a parent.
    """


class ModelNoParentDefinedError(ModelParentError):
    """
    ModelNoParentDefinedError is raised when an attempt is made to change the
    parent of an object that is not inlined and has no parent.
    """


class ModelParentTypeError(ModelParentError):
    """
    ModelParentTypeError is raised when an attempt to set the parent of an
    inline object is made with a parent of the wrong type.
    """


class ModelTypeError(TypeError):
    """
    ModelTypeError is raised by the Model meta-class during Model definition
    when there is an issue with the model.
    """
