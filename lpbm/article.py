# article.py - Article model.
# Author: Franck Michea < franck.michea@gmail.com >

# Python standart modules imports.
import datetime
import re
import os

# Internal modules imports.
import lpbm.constants

class Article(object):
    def __init__(self, filename):
        self.authors, self.categories, index = [], [], 0

        with open(filename) as f:
            article = f.readlines()

        # Parsing authors.
        frmt = re.compile('^author: (%s)$' % lpbm.constants.FRMT_LOGIN)
        match = frmt.match(article[index])
        while match is not None:
            self.authors.append(match.group(1))
            index += 1
            match = frmt.match(article[index])

        # Parsing categories
        frmt = re.compile('^category: (%s)$' % lpbm.constants.FRMT_CATEGORY)
        match = frmt.match(article[index])
        while match is not None:
            self.categories.append(match.group(1))
            index += 1
            match = frmt.match(article[index])

        # The rest is the article.
        self.content = ''.join(article[index:])

        # Getting some time informations.
        s = os.stat(filename)
        self.crt_date = datetime.datetime.fromtimestamp(s.st_ctime)
        self.mod_date = datetime.datetime.fromtimestamp(s.st_mtime)

class ArticlesManager(object):
    def __init__(self):
        self.articles = []

        for root, dirs, files in os.walk(lpbm.constants.ROOT_ARTICLES):
            for filename in files:
                if not filename.endswith('.markdown'):
                    continue
                self.articles.append(Article(os.path.join(root, filename)))
