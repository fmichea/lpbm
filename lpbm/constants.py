# constants.py - Constants used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import os
import string

# Formats used to check values.
FRMT_CATEGORY = '[a-zA-Z\| ]+'
FRMT_EMAIL = '[a-z\.A-Z0-9]+@[a-zA-Z0-9\.]+'
FRMT_LOGIN = '[a-zA-Z][a-zA-Z0-9]*'
FRMT_NAME = '[a-zA-Z ]+'
FRMT_DATE = '%B %d, %Y at %H:%M'

# Article slug configuration
SLUG_CHARS = string.lowercase + string.digits + '-'
SLUG_SIZE = 50

# Paths to find everything.
ROOT = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '..'
))
ROOT_TEMPLATES = os.path.join(ROOT, 'templates')
ROOT_STYLESHEETS = os.path.join(ROOT, 'stylesheets')

# Sources (added by user).
ROOT_SOURCES = os.path.join(ROOT, 'sources')
ROOT_SRC_AUTHORS = os.path.join(ROOT_SOURCES, 'authors')
ROOT_SRC_ARTICLES = os.path.join(ROOT_SOURCES, 'articles')
ROOT_SRC_STYLESHEETS = os.path.join(ROOT_SOURCES, 'stylesheets')

# Output directories (created by the script)
ROOT_OUTPUT = os.path.join(ROOT, 'result')
ROOT_OUTPUT_STYLESHEETS = os.path.join(ROOT_OUTPUT, 'stylesheets')
