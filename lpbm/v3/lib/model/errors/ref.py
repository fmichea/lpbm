from lpbm.v3.lib.model.base_ref import model_ref_name_id


class ModelRefError(Exception):
    """
    ModelRefError is a super-class of all errors raised from the ModelRef,
    including at definition and when referencing and de-referencing.
    """

    def __init__(self, owners, ref):
        super().__init__()
        self._owners = owners
        self._ref = ref

    def __str__(self):
        return '{owner}: error with reference {ref}'.format(
            owner=self._owners.clean_repr(),
            ref=model_ref_name_id(self._ref),
        )


class ModelRefInvalidClassError(ModelRefError):
    """
    ModelRefInvalidClassError is raised when loading a model and with model
    references of the wrong type in it.
    """

    def __init__(self, owner, ref, klass, klasses):
        super().__init__(owner, ref)
        self._klass, self._klasses = klass, klasses

    def __str__(self):
        klasses = ['"{klass}"'.format(klass=klass) for klass in self._klasses]
        error = ': object of type "{klass}" is not in {klasses}'.format(
            klass=self._klass, klasses=', '.join(klasses))
        return super().__str__() + error


class ModelRefDefinitionError(ModelRefError):
    """
    ModelRefDefinitionError is raised when defining a ModelRef (at Model
    declaration most likely) with invalid parameters, such as no class provided
    or one of the class provided is not a model.
    """

    def __init__(self, val):
        super().__init__(None, None)
        self._val = val

    def __str__(self):
        return self._val


class ModelRefNoSessionError(ModelRefError):
    """
    ModelRefNoSessionError is raised when referencing or de-referencing a
    ModelRef without a ModelSession, which is required for querying.
    """

    def __str__(self):
        return super().__str__() + ': no session provided when (de)referencing'


class ModelRefNotInSessionError(ModelRefError):
    """
    ModelRefNotInSessionError is raised when getting the ref to a model from a
    ModelRef but the object is not in the ModelSession.
    """

    def __str__(self):
        return super().__str__() + ': object referenced is not in session'
