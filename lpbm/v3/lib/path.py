import os
import warnings


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
    else:
        warnings.warn('got unknown file or unexpected file type.')


def listdir(rootdir):
    result = []
    for root, dirs, files in os.walk(rootdir):
        # Modifying the list in place to ignore all hidden directories.
        ignored_dirs = set()
        for idx, dirname in enumerate(dirs):
            if dirname.startswith('.'):
                ignored_dirs.add(idx)
        for idx in ignored_dirs:
            del dirs[idx]
        # Also ignoring all the hidden files.
        for filename in files:
            if filename.startswith('.'):
                continue
            filepath = os.path.join(root, filename)
            result.append(filepath[len(rootdir) + 1:])
    return result
