# tools.py - Tools that can be used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import os
import shutil

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

def input_default(prompt, default):
    '''
    Prompts the user for input, with a default value if nothing is given from
    the user.
    '''
    tmp = input('{prompt} [{default}]: '.format(
        prompt = prompt, default = default,
    ))
    if not tmp:
        tmp = default
    return tmp
