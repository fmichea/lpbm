# article.py - Article model.
# Author: Franck Michea < franck.michea@gmail.com >

# Python standart modules imports.
import datetime
import markdown
import re
import os
import codecs

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

        # The rest is the article.
        self.content = '\n'.join(article[index:])
        self.title_parts = []
        while re.match('^====*', article[index]) is None:
            self.title_parts.append(article[index])
            index += 1
        self.title = ' '.join(self.title_parts)

        # Generate a slug to use in the URL
        self.slug = '-'.join(s.lower() for s in self.title_parts if s)
        self.slug = self.slug.replace(' ', '-')
        self.slug = ''.join(c for c in self.slug
                              if c in lpbm.constants.SLUG_CHARS)
        self.slug = self.slug[:lpbm.constants.SLUG_SIZE]

        # Getting some time informations.
        s = os.stat(filename)
        self.crt_date = datetime.datetime.fromtimestamp(s.st_ctime)
        self.mod_date = datetime.datetime.fromtimestamp(s.st_mtime)

    def get_content(self):
        return markdown.markdown(self.content,
            ['codehilite(force_linenos=True)']
        )

    def get_filename(self):
        return os.path.join('articles', '%d.html' % self.pk)

    def get_url(self):
        return '%s?%s' % (self.get_filename(), self.slug)

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
