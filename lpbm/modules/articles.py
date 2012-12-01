# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Articles manager, finds and loads all the articles of the blog. These are a
pair of two files. One is a markdown file, the other one an ini file.
'''

import os
import subprocess
import sys

import lpbm.exceptions
import lpbm.logging
import lpbm.module_loader
import lpbm.tools as ltools

from lpbm.models.articles import Article

_LOGGER = lpbm.logging.get()

class Articles(lpbm.module_loader.ModelManagerModule):
    '''
    Articles manager, finds and loads all the articles of the blog. These are a
    pair of two files. One is a markdown file, the other one an ini file.
    '''

    # pylint: disable=C0321
    def abstract(self): return 'Loads and manipulates articles.'
    def model_cls(self): return Article
    def name(self): return 'articles'
    def object_name(self): return 'article'

    def init(self):
        super().init()

        self.needed_modules = ['authors', 'categories']

        self.add_id_option('-p', '--publish', help='Publishes the draft.')
        self.add_id_option('-E', '--edit-content', help='Opens your $EDITOR on the article.')

    def load(self, modules, args):
        f = lambda a: a.endswith('.markdown')
        for root, filename in ltools.filter_files(f, self.args.exec_path, 'articles'):
            self.register_object(Article, ltools.join(root, filename))

    def _get_author_verbose(self, authors):
        res = []
        for idx in authors:
            try:
                res.append(self.modules['authors'][idx].nickname)
            except lpbm.exceptions.ModelDoesNotExistError:
                pass
        return ltools.join_names(res or ['[deleted]'])

    # Particular functions for command line.
    def opt_list(self, *args, **kwargs):
        '''Lists all the articles with some useful information.'''
        super().opt_list(*args, **kwargs)
        if not kwargs.get('short', False):
            count, count_pub = 0, 0
            for article in self.objects:
                if not article.deleted:
                    count += 1
                    if article.published:
                        count_pub += 1
            print('    + {} article(s) available ({} published, {} drafts).'.format(
                count, count_pub, count - count_pub
            ))

    def opt_publish(self, id):
        '''Publish an article.'''
        article = self[id]
        article.publish()
        article.save()
        print('Article "{title}" by {authors} was published.'.format(
            title = article.title,
            authors = self._get_author_verbose(article.authors),
        ))

    def opt_new(self):
        '''
        New article from command line. This will help the user create a
        particular file.
        '''
        obj = super().opt_new()
        print('Article was successfully created!')
        if ltools.ask_sure(prompt='Do you want to edit it right now?'):
            self.opt_edit_content(obj.id)
        return obj

    def opt_edit_content(self, id):
        '''Opens editor to modify its content.'''
        article = self[id]
        subprocess.call('{editor} "{filename}"'.format(
            editor = os.environ.get('EDITOR', 'vim'),
            filename = article.path,
        ), shell=True)
