# constants.py - Constants used everywhere.
# Author: Franck Michea < franck.michea@gmail.com >

import os

# Formats used to check values.
FRMT_CATEGORY = '[a-zA-Z\| ]+'
FRMT_EMAIL = '[a-z\.A-Z0-9]+@[a-zA-Z0-9\.]+'
FRMT_LOGIN = '[a-zA-Z][a-zA-Z0-9]*'
FRMT_NAME = '[a-zA-Z ]+'
FRMT_DATE = '%B %d, %Y at %H:%M'

# Paths to find everything.
ROOT = os.path.realpath(os.path.join(
    os.path.dirname(__file__), '..'
))
ROOT_SOURCES = os.path.join(ROOT, 'sources')
ROOT_AUTHORS = os.path.join(ROOT_SOURCES, 'authors')
ROOT_ARTICLES = os.path.join(ROOT_SOURCES, 'articles')
ROOT_TEMPLATES = os.path.join(ROOT, 'templates')
ROOT_OUTPUT = os.path.join(ROOT, 'result')
ROOT_MEDIA = os.path.join(ROOT, 'media')
ROOT_STYLESHEETS = os.path.join(ROOT_MEDIA, 'stylesheets')
ROOT_JAVASCRIPT = os.path.join(ROOT_MEDIA, 'javascript')
