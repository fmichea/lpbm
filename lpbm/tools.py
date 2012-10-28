# tools.py - Tools that can be used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''This module provides some tools needed almost everywhere in the code.'''

import os
import re
import shutil
import sys

# pylint: disable=W0402
import string

_ROOT = os.path.join(os.path.dirname(__file__), '..')

def join(*args):
    '''Joins a some paths with ROOT as base path.'''
    return os.path.realpath(os.path.join(_ROOT, *args))

def filter_files(filter_fun, *path):
    '''Yields every filenames that match filter_fun in directories.'''
    root = os.path.join(*path)
    for root, directories, files in os.walk(root):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filter_fun(filepath):
                yield filepath

def mkdir_p(path):
    '''
    Emulates the behaviour of `mkdir -p` in shell (makes all the directories
    of the path specified.
    '''
    try:
        os.makedirs(path)
    except OSError:
        pass

def copy(src, dst):
    '''Copies the file from src to dst.'''
    shutil.copyfile(src, dst)

_SLUG_CHARS = string.ascii_lowercase + string.digits + '-'
_SLUG_SIZE = 50

def slugify(text):
    '''Returns the slug of a string (that can be used in an URL for example.'''
    slug = text.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c in _SLUG_CHARS)
    return slug[:_SLUG_SIZE]

def input_default(prompt, default, required=False, is_valid=None):
    '''
    Prompts the user for input, with a default value if nothing is given from
    the user.
    '''
    try:
        while True:
            tmp = input('{prompt}{required} [{default}]: '.format(
                prompt = prompt,
                default = default if default is not None else '',
                required = ' (required)' if required else '',
            ))
            if not tmp:
                tmp = default
            if (is_valid is None or is_valid(tmp)) and (not required or tmp):
                break
    except (KeyboardInterrupt, EOFError):
        sys.exit(1)
    return tmp

def ask_sure(default=False):
    '''
    Makes sure the user wants to proceed the following action. It returns True
    if user answers yes or y, else False.
    '''
    try:
        sure = input('Are you sure you want to proceed? [{default}] '.format(
            default = 'Y/n' if default else 'y/N',
        ))
    except (KeyboardInterrupt, EOFError):
        sys.exit('')
    return (not sure and default) or (sure.lower() in ['y', 'yes'])

def join_names(names):
    '''
    Returns a well formated list of names, ready for printing.

    Examples:
      - Trevor Reznik
      - Teddy and Leonard
      - Rita, Astor, Cody and Dexter
    '''
    if 1 < len(names):
        return ', '.join(sorted(names[:-1])) + ' and ' + names[-1]
    elif len(names) == 0:
        return '[deleted]'
    return names[0]

def split_on_comma(authors):
    '''Splits a string on commas and retrusn a set of the values.'''
    return (set(re.split(',[ \t]*', authors)) - set(['']))
