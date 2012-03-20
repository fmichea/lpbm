# config.py - Loads configuration.
# Author: Franck Michea < franck.michea@gmail.com >

import re
import os

import lpbm.constants

class Config(object):
    def __init__(self):
        try:
            with open(os.path.join(lpbm.constants.ROOT_SOURCES, 'config')) as f:
                lines = f.readlines()
        except IOError: lines = []

        # Get title of the blog.
        try: self.title = re.match('^title: (.+)$', lines[0]).group(1)
        except IndexError: self.title = 'No Title Defined'

        try: self.subtitle = re.match('^subtitle: (.+)$', lines[1]).group(1)
        except IndexError: self.subtitle = ''
