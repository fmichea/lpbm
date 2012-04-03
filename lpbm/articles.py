# article.py - Article model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

# Python standart modules imports.
import datetime
import markdown
import re
import os
import codecs
import jinja2

# Internal modules imports.
import lpbm.constants

class ArticleSameIdError(Exception):
    def __init__(self, art1, art2):
        self.art1, self.art2 = art1, art2

    def __repr__(self):
        return 'Articles `%s\' and `%s\' have the same id defined.' % (
            self.art1.filename, self.art2.filename
        )

class Article(object):
    def __init__(self, filename, aut_mgr, cat_mgr):
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
            cat_mgr.parse_category(match.group(1))
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
        self.slug = self.slug.lower().replace(' ', '-')
        self.slug = ''.join(c for c in self.slug
                              if c in lpbm.constants.SLUG_CHARS)
        self.slug = self.slug[:lpbm.constants.SLUG_SIZE]

        # The rest is the article.
        self.content = '\n'.join(article[index:])

    def get_content(self):
        return markdown.markdown(self.content,
            ['codehilite(force_linenos=True)']
        )

    def get_filename(self):
        return os.path.join('articles', '%d-%s.html' % (self.pk, self.slug))

    def get_url(self):
        return ('/%s' % self.get_filename())

    def get_authors(self):
        template = jinja2.Environment(loader=jinja2.FileSystemLoader(
            lpbm.constants.ROOT_TEMPLATES
        )).get_template(os.path.join('authors', 'link.html'))
        return ', '.join([
            template.render({'author': self.aut_mgr.authors[author]})
            for author in self.authors
        ])

    def get_date(self):
        return self.crt_date.strftime(lpbm.constants.FRMT_DATE)


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
                        raise ArticleSameId(self.articles[a.pk], a)
                    else:
                        self.articles[a.pk] = a

    def get_articles(self):
        return sorted(self.articles.values(), cmp=lambda a, b: -cmp(a.pk, b.pk))

    def render(self, template):
        template.init_template('articles', 'base.html')

        # Render all articles
        for article in self.articles.values():
            template.render(article.get_filename(), {
                'articles': [article],
                'comments_enabled': True,
            })
