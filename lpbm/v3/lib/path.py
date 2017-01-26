import os


_EXEC_PATH = None


def initialize(ctx):
    global _EXEC_PATH
    _EXEC_PATH = ctx.obj['exec-path']


def in_blog_join(*args):
    assert _EXEC_PATH is not None
    return os.path.join(_EXEC_PATH, *args)


def full_split(path):
    parts, head = [], None
    while head != '':
        head, tail = os.path.split(path)
        parts.append(tail)
        path = head
    return parts


def mkdir_p(path):
    """
    Emulates the behaviour of `mkdir -p` in shell (makes all the directories
    of the path specified).
    """
    try:
        os.makedirs(path)
    except OSError:
        pass


def remove(path):
    if os.path.isfile(path):
        os.remove(path)
    elif os.path.isdir(path):
        os.rmdir(path)
