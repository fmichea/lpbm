# path.py - Manipulates paths and lists files.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Helper tools on paths to reference and walk through blog sources absolutely
to script position.
'''

import os

_ROOT = os.path.join(os.path.dirname(__file__), '..')

def join(*args):
    '''Joins a some paths with ROOT as base path.'''
    return os.path.realpath(os.path.join(_ROOT, *args))

def filter_files(filter_fun, *directories):
    '''Yields every filenames that match filter_fun in directories.'''
    root = os.path.join(_ROOT, *directories)
    for root, directories, files in os.walk(root):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filter_fun(filepath):
                yield filepath
