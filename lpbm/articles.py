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

from datetime import datetime
import configparser

class ArticleSameIdError(Exception):
    def __init__(self, art1, art2):
        self.art1, self.art2 = art1, art2

    def __str__(self):
        return 'Articles `%s\' and `%s\' have the same id defined.' % (
            self.art1.title, self.art2.title
        )

CONFIG_SEPARATOR = '+' * 72
TITLE_SEPARATOR = '=='

class Article(object):
    def __init__(self, filename):
        self.filename = filename
        config, self.title, self.raw_content = '', '', ''
        self.config = configparser.ConfigParser()

        # Reads the content of the file, config being before SEPARATOR
        try:
            f = codecs.open(filename, 'r', 'utf-8')
        except IOError:
            return

        # Reading the content of the file.
        line = f.readline()
        while line:
            if line.startswith(CONFIG_SEPARATOR):
                line = f.readline()
                break
            config += line
            line = f.readline()
        while line:
            if line.startswith(TITLE_SEPARATOR):
                line = f.readline()
                break
            self.title += line[:-1]
            line = f.readline()
        while line:
            self.raw_content += line
            line = f.readline()

        # Parse configuration.
        self.config.read_string(config)

    def __lt__(self, other):
        return self.raw_date() < other.raw_date()

    def save(self):
        f = codecs.open(self.filename, 'w', 'utf-8')
        self.config.write(f)
        f.write(CONFIG_SEPARATOR + '\n')

        # Then we have the title.
        f.write(self.title + '\n')
        f.write(len(self.title) * '=' + '\n')

        # End finally we have the content.
        f.write(self.raw_content)
        f.close()

    def id(self):
        return self.config.getint('general', 'id', fallback=-1)

    def published(self):
        return self.config.getboolean('general', 'published', fallback=False)

    def authors(self):
        authors = self.config.get('general', 'authors', fallback='NOTSET')
        return re.split(',[ \t]*', authors)

    def slug(self):
        slug = self.config.get('general', 'slug', fallback=None)
        if slug is None:
            self.slug = self.title.lower().replace(' ', '-')
            self.slug = ''.join(c for c in self.slug
                                if c in lpbm.constants.SLUG_CHARS)
            self.slug = self.slug[:lpbm.constants.SLUG_SIZE]
        return slug

    def content(self):
        return markdown.markdown(self.raw_content,
            ['codehilite(force_linenos=True)']
        )

    def raw_date(self):
        date = self.config.get('general', 'date', fallback='')
        try:
            return datetime.strptime(date, lpbm.constants.FRMT_DATE_CONF)
        except ValueError:
            return datetime.fromtimestamp(0)

    def date(self):
        return self.raw_date().strftime(lpbm.constants.FRMT_DATE)

    def html_filename(self):
        return os.path.join('articles', '%d-%s.html' % (self.pk, self.slug))

    def url(self):
        return ('/%s' % self.html_filename())

    def publish(self):
        self.config.set('general', 'published', 'yes')
        self.config.set('general', 'date', datetime.now().strftime(
            lpbm.constants.FRMT_DATE_CONF
        ))

    def create(self, pk, title, authors):
        self.config.add_section('general')
        self.config.set('general', 'id', str(pk))
        self.config.set('general', 'published', 'no')
        self.config.set('general', 'authors', authors)
        self.title = title

    # FIXME: aut_mgr doesn't exist.
    def _render_authors(self):
        template = jinja2.Environment(loader=jinja2.FileSystemLoader(
            lpbm.constants.ROOT_TEMPLATES
        )).get_template(os.path.join('authors', 'link.html'))
        return ', '.join([
            template.render({'author': self.aut_mgr.authors[author]})
            for author in self.authors
        ])

    # FIXME: Remove all this part when done.
    def ex__init__(self, filename, aut_mgr, cat_mgr):
        self.filename = 0
        self.authors, self.categories, self.aut_mgr, index = [], [], aut_mgr, 0

        f = codecs.open(filename, 'r', 'utf-8')
        article = map(lambda a: a[:-1] if a[-1] == '\n' else a, f.readlines())

        # Finding if the article has an id.
        match = re.match('^id: ([0-9]+)$', article[index])
        if match is not None:
            self.pk = int(match.group(1))
            index += 1
        else:
            self.pk = None

        # Parsing authors.
        frmt = re.compile('^author: (%s)$' % lpbm.constants.FRMT_LOGIN)
        match = frmt.match(article[index])
        while match is not None:
            self.authors.append(match.group(1))
            self.aut_mgr.add_author(match.group(1))
            index += 1
            match = frmt.match(article[index])

        # Parsing categories
        frmt = re.compile('^category: (%s)$' % lpbm.constants.FRMT_CATEGORY)
        match = frmt.match(article[index])
        while match is not None:
            self.categories.append(match.group(1))
            cat_mgr.parse_category(match.group(1)).articles.append(self)
            index += 1
            match = frmt.match(article[index])

        # Parsing the title.
        match = re.match('^title: (.+)$', article[index])
        if match is None: self.title = 'FIXME: No Title.'
        else:
            self.title = match.group(1)
            index += 1

        # Getting some time informations.
        s = os.stat(filename)
        self.crt_date = datetime.datetime.fromtimestamp(s.st_ctime)
        self.mod_date = datetime.datetime.fromtimestamp(s.st_mtime)

        # Parsing the pubdate.
        match = re.match('^pubdate: (.+)$', article[index])
        if match is not None:
            self.crt_date = datetime.datetime.strptime(
                match.group(1),
                "%Y-%m-%dT%H:%M:%S"
            )
            index += 1

        # Generate a slug to use in the URL
        match = re.match('^slug: (.+)$', article[index])
        if match is not None:
            self.slug = match.group(1)
            index += 1
        else: self.slug = self.title

        # The rest is the article.
        self.content = '\n'.join(article[index:])

    def get_content(self):
        return markdown.markdown(self.content,
            ['codehilite(force_linenos=True)']
        )



class ArticlesManager(object):
    def __init__(self, aut_mgr, cat_mgr):
        self.articles = dict()

        for root, dirs, files in os.walk(lpbm.constants.ROOT_SRC_ARTICLES):
            for filename in files:
                if not filename.endswith('.markdown'):
                    continue
                a = Article(os.path.join(root, filename), aut_mgr, cat_mgr)
                if a.pk is not None:
                    if a.pk in self.articles:
                        raise ArticleSameIdError(self.articles[a.pk], a)
                    else:
                        self.articles[a.pk] = a

    def get_articles(self):
        return sorted(self.articles.values())

    def render(self, template):
        template.init_template('articles', 'base.html')

        # Render all articles
        for article in self.articles.values():
            template.render(article.get_filename(), {
                'page_title': article.title,
                'articles': [article],
                'comments_enabled': True,
            })
