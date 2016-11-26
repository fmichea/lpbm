import os


_EXEC_PATH = None


def initialize(ctx):
    global _EXEC_PATH
    _EXEC_PATH = ctx.obj['exec-path']


def in_blog_join(*args):
    assert _EXEC_PATH is not None
    return os.path.join(_EXEC_PATH, *args)
