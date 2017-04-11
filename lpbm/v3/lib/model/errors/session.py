class ModelSessionError(Exception):
    """
    ModelSessionError is a super-class of all exceptions raised related to
    ModelSession issues.
    """


class ModelSessionBlogLockedError(ModelSessionError):
    """
    ModelSessionBlogLockedError is raised when trying to create a read-write
    session on the blog while another instance of lpbm already has a read-write
    session open.

    This is currently not possible to avoid inconsistencies in data.
    """


class ModelSessionReadOnlyError(Exception):
    """
    ModelSessionReadOnlyError is raised when trying to commit a read-only
    session, which is not allowed.
    """
