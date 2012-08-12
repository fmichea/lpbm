# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import datetime
import os
import subprocess
import sys

import lpbm.articles
import lpbm.logging
import lpbm.module_loader
import lpbm.path

_LOGGER = lpbm.logging.get()

class Articles(lpbm.module_loader.Module):
    def name(self): return 'articles'
    def abstract(self): return 'Loads, manipulates and renders articles.'

    def init(self):
        self.parser.add_argument('-l', '--list', action='store_true',
                                 help='List the articles by title.')
        self.parser.add_argument('-a', '--article', action='store', type=int,
                                 metavar='id', default=None,
                                 help='Select an article for several options.')
        self.parser.add_argument('-p', '--publish', action='store_true',
                                 help='Publishes the draft.')
        self.parser.add_argument('-P', '--preview', action='store_true',
                                 help='Only renders draft articles.')
        self.parser.add_argument('-n', '--new', action='store', metavar='filename',
                                 help='Help create a new draft. ' + \
                                      '(path/to/articles/ARGUMENT.markdown)')

    def process(self, modules, args):
        self.args = args
        if args.list:
            self.list_articles()
        elif args.publish:
            self.publish_article()
        elif args.preview:
            self.preview_articles()
        elif args.new:
            self.new_article(args.new)

    # Methods to manipulate articles.
    def get_articles_list(self):
        f, articles = lambda a: a.endswith('.markdown'), []
        for f in lpbm.path.filter_files(f, self.args.exec_path, 'articles'):
            articles.append(lpbm.articles.Article(f))
        return sorted(articles)

    def check_article_selected(self, option):
        if self.args.article is None:
            sys.exit('Option `{}` needs an aricle selected.'.format(option))

    # Particular functions for command line.
    def list_articles(self):
        count, count_pub, articles = 0, 0, self.get_articles_list()
        print('All articles:')
        for article in reversed(articles):
            print(' {id:2d} + "{title}" by {authors} [{published}]'.format(
                id = article.id(), title = article.title,
                authors = ', '.join(article.authors()),
                published = 'published' if article.published() else 'draft',
            ))
            count += 1
            if article.published():
                count_pub += 1
        print('    + {} article(s) available ({} published, {} drafts).'.format(
            count, count_pub, count - count_pub
        ))

    def publish_article(self):
        self.check_article_selected('publish')
        try:
            article = list(filter(lambda a: a.id() == self.args.article,
                                   self.get_articles_list()))[0]
            article.publish()
            article.save()
            print('Article "{title}" by {authors} was published.'.format(
                title = article.title,
                authors = ', '.join( article.authors()),
            ))
        except IndexError:
            sys.exit('This article doesn\'t exist.')

    def preview_articles(self):
        self.check_article_selected('preview')
        # FIXME

    def new_article(self, filename):
        # First we check that file doesn't exist.
        path = lpbm.path.join(
            self.args.exec_path, 'articles', '{}.markdown'.format(filename)
        )
        if os.path.exists(path):
            sys.exit('File `{}\' exists, please choose a different name.'.format(
                path
            ))
        # Then we check if we want to use the first available id.
        ids, pk = list(map(lambda a: a.id(), self.get_articles_list())), None
        last_id = max(ids) + 1
        while pk is None:
            try:
                pk = int(input('Please enter an id [{}]: '.format(last_id)))
                if pk in ids:
                    print('Id already exists, please choose a different one.')
                    pk = None
            except ValueError:
                pk = last_id

        # Then we want a title.
        title = input('Please enter a title: ')
        authors = input('Please list authors (comma separated): ')
        article = lpbm.articles.Article(path)
        article.create(pk, title, authors)
        article.save()

        # We successfully created article.
        print('Article `{}\' was successfully created!'.format(path))

        # Why not edit right away?
        edit = input('Do you want to edit this article right now? [y/N] ')
        if edit.lower() == 'y':
            subprocess.call('{editor} "{filename}"'.format(
                editor = os.environ.get('EDITOR', 'vim'),
                filename = path,
            ), shell=True)
