# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Articles manager, finds and loads all the articles of the blog. These are a
pair of two files. One is a markdown file, the other one an ini file.
'''

import lpbm.exceptions
import lpbm.logging
import lpbm.module_loader
import lpbm.tools as ltools

from lpbm.lib.deprecated_command import deprecated_command
from lpbm.models.articles import Article


_LOGGER = lpbm.logging.get()


class Articles(lpbm.module_loader.ModelManagerModule):
    '''
    Articles manager, finds and loads all the articles of the blog. These are a
    pair of two files. One is a markdown file, the other one an ini file.
    '''

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
        def filter_fn(a):
            return a.endswith('.markdown')

        for root, filename in ltools.filter_files(filter_fn, self.args.exec_path, 'articles'):
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
        deprecated_command()

    def opt_publish(self, id):
        '''Publish an article.'''
        deprecated_command()

    def opt_new(self):
        '''
        New article from command line. This will help the user create a
        particular file.
        '''
        deprecated_command()

    def opt_edit_content(self, id):
        '''Opens editor to modify its content.'''
        deprecated_command()
