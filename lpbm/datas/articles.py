# article.py - Article model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

# Python standart modules imports.
import codecs
import jinja2
import markdown
import math
import os
import re

# Internal modules imports.
import lpbm.constants

import lpbm.datas.configmodel as cm_module

from datetime import datetime
import configparser

class ArticleSameIdError(Exception):
    def __init__(self, art1, art2):
        self.art1, self.art2 = art1, art2

    def __str__(self):
        return 'Articles `%s\' and `%s\' have the same id defined.' % (
            self.art1.title, self.art2.title
        )

TITLE_SEPARATOR = '=='

class Article:
    id = cm_module.opt_int('general', 'id', default=-1)
    published = cm_module.opt_bool('general', 'published', default=False)

    _date = cm_module.opt('general', 'date')
    _slug = cm_module.opt('general', 'slug')
    _authors = cm_module.opt('general', 'authors', default='')

    def __init__(self, filename):
        '''
        Articles are devided in two files. The actual article (written in
        markdown syntax) and a configuration file containing information for
        blog generation.
        '''
        self._filename, self.title, self._content = filename[:-9], '', ''
        self.path = filename

        # Reads the content of the file, config being before SEPARATOR
        try:
            f = codecs.open(filename, 'r', 'utf-8')
            line = f.readline()
            while line:
                if line.startswith(TITLE_SEPARATOR):
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
            self.date = datetime.now()

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

    def _split_authors_string(self, authors):
        return (set(re.split(',[ \t]*', authors)) - set(['']))

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
        self._authors_set |= self._split_authors_string(authors)

    def remove_authors(self, authors):
        '''
        Takes a string of comma-separated authors and removes them from authors
        list for the article.
        '''
        self._authors_set -= self._split_authors_string(authors)

    @property
    def slug(self):
        return self._slug

    @slug.setter
    def slug(self, value):
        if value is None:
            self._slug = None
        else:
            self._slug = lpbm.tools.slugify(value)

    @property
    def date(self):
        try:
            return datetime.strptime(self._date, lpbm.constants.FRMT_DATE_CONF)
        except ValueError:
            return datetime.fromtimestamp(0)

    @date.setter
    def date(self, value):
        if value is None:
            self._date = None
        else:
            self._date = value.strftime(lpbm.constants.FRMT_DATE_CONF)

    def content(self):
        opt = 'codehilite(force_linenos=True)'
        return markdown.markdown(self._content, [opt])

    def _config_filename(self):
        return '{filename}.cfg'.format(filename = self._filename)

    def _markdown_filename(self):
        return '{filename}.markdown'.format(filename = self._filename)

    def html_filename(self):
        slug = self._slug
        if slug is None:
            slug = lpbm.tools.slugify(self._title)
        return os.path.join('articles', '%d-%s.html' % (self.pk, slug))

    def url(self):
        '''The direct link to the article.'''
        return ('/%s' % self.html_filename())

    def publish(self):
        self.published = True
        self.date = datetime.now()

# FIXME: aut_mgr doesn't exist.
#    def _render_authors(self):
#        template = jinja2.Environment(loader=jinja2.FileSystemLoader(
#            lpbm.constants.ROOT_TEMPLATES
#        )).get_template(os.path.join('authors', 'link.html'))
#        return ', '.join([
#            template.render({'author': self.aut_mgr.authors[author]})
#            for author in self.authors
#        ])


# FIXME: Remove me.
#class ArticlesManager(object):
#    def __init__(self, aut_mgr, cat_mgr):
#        self.articles = dict()
#
#        for root, dirs, files in os.walk(lpbm.constants.ROOT_SRC_ARTICLES):
#            for filename in files:
#                if not filename.endswith('.markdown'):
#                    continue
#                a = Article(os.path.join(root, filename), aut_mgr, cat_mgr)
#                if a.pk is not None:
#                    if a.pk in self.articles:
#                        raise ArticleSameIdError(self.articles[a.pk], a)
#                    else:
#                        self.articles[a.pk] = a
#
#    def get_articles(self):
#        return sorted(self.articles.values())
#
#    def render(self, template):
#        template.init_template('articles', 'base.html')
#
#        # Render all articles
#        for article in self.articles.values():
#            template.render(article.get_filename(), {
#                'page_title': article.title,
#                'articles': [article],
#                'comments_enabled': True,
#            })
