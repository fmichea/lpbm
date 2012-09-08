# tools.py - Tools that can be used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import os
import shutil

def mkdir_p(path):
    try: os.makedirs(path)
    except OSError: pass

def cp(src, dst):
    shutil.copyfile(src, dst)

def slugify(text):
    slug = text.lower().replace(' ', '-')
    slug = ''.join(c for c in slug if c in lpbm.constants.SLUG_CHARS)
    return slug[:lpbm.constants.SLUG_SIZE]

def input_default(prompt, default):
    tmp = input('{prompt} [{default}]: '.format(
        prompt = prompt, default = default,
    ))
    if not tmp:
        tmp = default
    return tmp
