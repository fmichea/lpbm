# tools.py - Tools that can be used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import os
import shutil
import sys

import lpbm.constants

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

def slugify(text):
    '''Returns the slug of a string (that can be used in an URL for example.'''
    slug = text.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c in lpbm.constants.SLUG_CHARS)
    return slug[:lpbm.constants.SLUG_SIZE]

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
    try:
        sure = input('Are you sure you want to proceed? [{default}] '.format(
            default = 'Y/n' if default else 'y/N',
        ))
    except (KeyboardInterrupt, EOFError):
        sys.exit('')
    return (not sure and default) or (sure.lower() == 'y')
