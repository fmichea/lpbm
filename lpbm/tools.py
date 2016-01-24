# tools.py - Tools that can be used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''This module provides some tools needed almost everywhere in the code.'''

import os
import re
import shutil
import sys


ROOT = os.path.dirname(__file__)


def abspath(*args):
    '''Wrapper doing nothing for now.'''
    return os.path.abspath(*args)


def join(*args):
    '''Joins a some paths with ROOT as base path.'''
    return os.path.realpath(os.path.join(*args))


def filter_files(filter_fun, *path):
    '''Yields every filenames that match filter_fun in directories.'''
    root = join(*path)
    root_len = len(root)
    for subroot, directories, files in os.walk(root):
        for filename in files:
            if filter_fun(filename):
                yield (root, os.path.join(subroot[root_len + 1:], filename))


def mkdir_p(path):
    '''
    Emulates the behaviour of `mkdir -p` in shell (makes all the directories
    of the path specified.
    '''
    try:
        os.makedirs(path)
    except OSError:
        pass


def empty_directory(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        for f in files:
            os.unlink(join(root, f))
        for d in dirs:
            os.rmdir(join(root, d))


def move_content(src, dst):
    for root, dirs, files in os.walk(src):
        for f in (files + dirs):
            shutil.move(join(root, f), dst)
        while dirs:
            dirs.pop()


def copy(src, dst):
    '''Copies the file from src to dst.'''
    mkdir_p(os.path.dirname(dst))
    shutil.copyfile(src, dst)


def input_default(prompt, default, required=False, is_valid=None):
    '''
    Prompts the user for input, with a default value if nothing is given from
    the user.
    '''
    try:
        while True:
            tmp = input('{prompt}{required} [{default}]: '.format(
                prompt=prompt,
                default=default if default is not None else '',
                required=' (required)' if required else '',
            ))
            if not tmp:
                tmp = default
            if (not required or tmp is not None) and (is_valid is None or is_valid(tmp)):
                break
    except KeyboardInterrupt:
        sys.exit(1)
    except EOFError:
        if (
            not required and
            default is not None and
            ask_sure(prompt='Deleting field content.', default=True)
        ):
            return None
        sys.exit(1)
    return tmp


def ask_sure(prompt='Are you sure you want to proceed?', default=False):
    '''
    Makes sure the user wants to proceed the following action. It returns True
    if user answers yes or y, else False.
    '''
    try:
        sure = input('{prompt} [{default}] '.format(
            prompt=prompt,
            default=('Y/n' if default else 'y/N'),
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
