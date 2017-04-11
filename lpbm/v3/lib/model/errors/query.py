class ModelQueryError(Exception):
    """
    ModelQueryError is a super-class of all query related exceptions that can
    be raised when using the ModelQuery object to load object in the session.
    """


class ModelQueryInvalidCriterionError(ModelQueryError):
    """
    ModelQueryInvalidCriterionError is raised when using filter/order_by on a
    query but the criterion is invalid. See each function's documentation for
    expected criterion types.
    """


class ModelQueryNoObjectFoundError(ModelQueryError):
    """
    ModelQueryNoObjectFoundError is raised when query-ing for one/the first
    object but no object could really be found.
    """


class ModelQueryNoParentError(ModelQueryError):
    """
    ModelQueryNoParentError is raised when trying to set the parent on a query
    for a model that is not an inline object.
    """


class ModelQueryParentAlreadySetError(ModelQueryError):
    """
    ModelQueryParentAlreadySetError is raised when trying to set the parent
    twice on an inline model query.
    """


class ModelQueryParentWrongTypeError(ModelQueryError):
    """
    ModelQueryParentWrongTypeError is raised when trying to set the parent of
    an inline model's query with the wrong parent type.
    """


class ModelQueryTooManyObjectsError(ModelQueryError):
    """
    ModelQueryTooManyObjectsError is raised when query-ing for exactly one
    object but multiple objects where found.
    """
