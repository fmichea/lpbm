# article.py - Article model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''This module contains the data model for Articles in blog sources.'''

import codecs
import datetime
import os
import re

import lpbm.datas.configmodel as cm_module
import lpbm.tools

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

class Article:
    '''
    The actual model. Articles are devided in two files. The actual article
    (written in markdown syntax) and a configuration file containing information
    for blog generation.
    '''

    id = cm_module.opt_int('general', 'id', default=-1)
    published = cm_module.opt_bool('general', 'published', default=False)

    _date = cm_module.opt('general', 'date')
    _slug = cm_module.opt('general', 'slug')
    _authors = cm_module.opt('general', 'authors', default='')

    def __init__(self, filename):
        self._filename, self.title, self._content = filename[:-9], '', ''
        self.path = filename

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
        except IOError:
            pass

        # Parse configuration.
        self.cm = cm_module.ConfigModel(self._config_filename())

        # Authors
        self._authors_set = set()
        self.add_authors(self._authors)

        # If creating the article, set date to now.
        if self._date is None:
            self.date = datetime.datetime.now()

    def __lt__(self, other):
        '''Articles are sorted by date'''
        return self.date < other.date or self.id < other.id

    def save(self):
        '''Articles' configuration is saved automatically.'''
        with codecs.open(self._markdown_filename(), 'w', 'utf-8') as f:
            # Then we have the title.
            f.write(self.title + '\n')
            f.write(len(self.title) * '=' + '\n')

            # End finally we have the content.
            f.write(self._content)

        # Saving configuration
        self._authors = ', '.join(list(self._authors_set))
        self.cm.save()

    @property
    def authors(self):
        '''Returns the list of authors.'''
        return list(self._authors_set)

    def authors_list(self):
        '''
        Returns a well formated list of authors, ready for printing.

        Examples:
          - Trevor Reznik
          - Teddy and Leonard
          - Rita, Astor, Cody and Dexter
        '''
        authors = list(self._authors_set)
        if 1 < len(authors):
            return ', '.join(authors[:-1]) + ' and ' + authors[-1]
        elif len(authors) == 0:
            return '[no author]'
        return authors[0]

    def add_authors(self, authors):
        '''
        Takes a string of comma-separated authors and adds them to authors of
        the article.
        '''
        self._authors_set |= _split_authors_string(authors)

    def remove_authors(self, authors):
        '''
        Takes a string of comma-separated authors and removes them from authors
        list for the article.
        '''
        self._authors_set -= _split_authors_string(authors)

    @property
    def slug(self):
        '''
        Returns the slug of the article (this is the getter of the property).
        '''
        return self._slug

    @slug.setter
    def slug(self, value):
        '''
        Sets the slug of the article, which means it won't change if the
        article title changes. (to keep url with a slug and still be able to
        edit article's title).
        '''
        if value is None:
            self._slug = None
        else:
            self._slug = lpbm.tools.slugify(value)

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
        return '{filename}.cfg'.format(filename = self._filename)

    def _markdown_filename(self):
        '''Returns the filename with markdown's extension.'''
        return '{filename}.markdown'.format(filename = self._filename)

    def html_filename(self):
        '''Returns the filename of the HTML file for that article.'''
        slug = self._slug
        if slug is None:
            slug = lpbm.tools.slugify(self.title)
        return '%d-%s.html' % (self.id, slug)

    def url(self):
        '''The direct link to the article.'''
        return os.path.join('/', 'articles', self.html_filename())

    def publish(self):
        '''
        Set everything needed to publish an article (published flag and date).
        '''
        self.published = True
        self.date = datetime.datetime.now()


def _split_authors_string(authors):
    '''Splits a string on commas and retrusn a set of the values.'''
    return (set(re.split(',[ \t]*', authors)) - set(['']))
