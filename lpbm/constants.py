# constants.py - Constants used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >

import os

# Formats used to check values.
FRMT_CATEGORY = '[a-zA-Z\| ]+'
FRMT_EMAIL = '[a-z\.A-Z0-9]+@[a-zA-Z0-9\.]+'
FRMT_LOGIN = '[a-zA-Z][a-zA-Z0-9]*'
FRMT_NAME = '[a-zA-Z ]+'

# Paths to find everything.
ROOT = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '..', 'sources'
))
ROOT_AUTHORS = os.path.join(ROOT, 'authors')
ROOT_ARTICLES = os.path.join(ROOT, 'articles')
