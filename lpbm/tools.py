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
