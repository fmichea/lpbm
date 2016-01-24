# article.py - Article model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''This module contains the data model for Articles in blog sources.'''

import codecs
import datetime
import os

import lpbm.models.configmodel as cm_module
import lpbm.tools as ltools

from lpbm.lib.slugify import (
    SLUG_CHARS_DISPLAY as _SLUG_CHARS_DISPLAY,
    slugify as _slugify,
)


class ArticleSameIdError(Exception):
    '''Exception raised when two articles are found with the same id.'''

    def __init__(self, art1, art2):
        super(ArticleSameIdError, self).__init__(self)
        self.art1, self.art2 = art1, art2

    def __str__(self):
        return 'Articles `%s\' and `%s\' have the same id defined.' % (
            self.art1.title, self.art2.title
        )


_TITLE_SEPARATOR = '=='
_FRMT_DATE_CONF = '%Y-%m-%dT%H:%M:%S'


class Article(cm_module.Model):
    '''
    The actual model. Articles are devided in two files. The actual article
    (written in markdown syntax) and a configuration file containing information
    for blog generation.
    '''

    title = cm_module.field('title', required=True)
    published = cm_module.opt_bool('general', 'published', default=False)

    _date = cm_module.opt('general', 'date')
    _authors = cm_module.opt('general', 'authors', default='')
    _categories = cm_module.opt('general', 'categories', default='')

    def __init__(self, mod, mods, filename=None):
        super().__init__(mod, mods)

        self.title, self._content = '', ''
        try:
            self.filename, self.path = filename[:-9], filename
        except TypeError:
            self.filename, self.path = '', ''

        # Reads the content of the file, config being before SEPARATOR
        try:
            f = codecs.open(filename, 'r', 'utf-8')
            line = f.readline()
            while line:
                if line.startswith(_TITLE_SEPARATOR):
                    line = f.readline()
                    break
                self.title += line[:-1]
                line = f.readline()
            while line:
                self._content += line
                line = f.readline()
        except (IOError, TypeError):
            pass

        # Model configuration.
        self.cm = cm_module.ConfigModel(self._config_filename())

        # Interactive fields.
        self._interactive_fields = ['title']
        if self.id is None:
            self._interactive_fields += ['filename']
        self._interactive_fields += ['authors', 'categories']

        # Authors
        self.authors = self._authors
        self.categories = self._categories

        # If creating the article, set date to now.
        if self._date is None:
            self.date = datetime.datetime.now()

    def __str__(self):
        return '"{title}" by {authors} [{published}]'.format(
            id=self.id,
            title=self.title,
            authors=self.mod._get_author_verbose(self.authors),
            published=('published' if self.published else 'draft'),
        )

    def __lt__(self, other):
        '''Articles are sorted by date'''
        return (self.date, self.id) < (other.date, other.id)

    def save(self):
        '''Articles' configuration is saved automatically.'''
        with codecs.open(self._markdown_filename(), 'w', 'utf-8') as f:
            # Then we have the title.
            f.write(self.title + '\n')
            f.write(len(self.title) * '=' + '\n')

            # End finally we have the content.
            f.write(self._content)

        # Saving special fields configuration
        self._authors = ', '.join(list(self._authors_set))
        self._categories = ', '.join(list(self._categories_set))

        # Finally saving everything.
        super().save()

    def interactive_filename(self):
        def is_valid(value):
            if _slugify(value) != value:
                print('This is not a valid slug ({}).'.format(_SLUG_CHARS_DISPLAY))
                return False
            path = os.path.join('articles', value + '.markdown')
            if os.path.exists(os.path.normpath(path)):
                print('Article with this filename already exists.')
                return False
            return True
        default = _slugify(self.title)
        self.filename = ltools.input_default(
            'Filename', default, required=True, is_valid=is_valid)

        # Several paths have to be reset.
        self.filename = os.path.join('articles', self.filename)
        self.path = os.path.normpath(self.filename + '.markdown')
        self.cm.filename = self._config_filename()

    def interactive_authors(self):
        self.mods['authors'].opt_list(short=True)
        self.authors = ltools.input_default(
            'Please list authors (comma separated)', self._authors,
            required=True, is_valid=self.mods['authors'].is_valid_list,
        )

    def interactive_categories(self):
        self.mods['categories'].opt_list(short=True)
        self.categories = ltools.input_default(
            'Please list categories (comma separated)', self._categories,
            required=True, is_valid=self.mods['categories'].is_valid_list,
        )

    def delete(self):
        super().delete()
        self.published = False

    @property
    def authors(self):
        '''Returns the list of authors.'''
        return [int(a) for a in list(self._authors_set)]

    @authors.setter
    def authors(self, authors):
        '''
        Takes a string of comma-separated authors and adds them to authors of
        the article.
        '''
        self._authors_set = set(ltools.split_on_comma(authors))

    @property
    def categories(self):
        return [int(c) for c in list(self._categories_set)]

    @categories.setter
    def categories(self, value):
        self._categories_set = set(ltools.split_on_comma(value))

    @property
    def date(self):
        '''Translates date string in configuration to a timestamp. (getter).'''
        try:
            return datetime.datetime.strptime(self._date, _FRMT_DATE_CONF)
        except ValueError:
            return datetime.datetime.fromtimestamp(0)

    @date.setter
    def date(self, value):
        '''Translates a date as a string in the right format. (setter).'''
        if value is None:
            self._date = None
        else:
            self._date = value.strftime(_FRMT_DATE_CONF)

    @property
    def content(self):
        return self._content

    def _config_filename(self):
        '''Returns the filename with config's extension.'''
        return '{filename}.cfg'.format(filename=self.filename)

    def _markdown_filename(self):
        '''Returns the filename with markdown's extension.'''
        return '{filename}.markdown'.format(filename=self.filename)

    def html_filename(self):
        '''Returns the filename of the HTML file for that article.'''
        filename = os.path.basename(self.filename)
        return '%d-%s.html' % (self.id, filename)

    def url(self):
        '''The direct link to the article.'''
        return os.path.join('/', 'articles', self.html_filename())

    def publish(self):
        '''
        Set everything needed to publish an article (published flag and date).
        '''
        self.published = True
        self.date = datetime.datetime.now()
