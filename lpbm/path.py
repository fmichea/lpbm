# path.py - Manipulates paths and lists files.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import os

_ROOT = os.path.join(os.path.dirname(__file__), '..')

def join(*args):
    return os.path.realpath(os.path.join(_ROOT, *args))

def filter_files(filter_fun, *directories):
    root = os.path.join(_ROOT, *directories)
    for root, directories, files in os.walk(root):
        for f in files:
            filepath = os.path.join(root, f)
            if filter_fun(filepath):
                yield filepath
