# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import jinja2
import markdown
import os
import tempfile

import lpbm.module_loader
import lpbm.tools as ltools

_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(
    lpbm.tools.join('medias', 'templates')
))

def _get_template(*args):
    return _ENV.get_template(os.path.join(*args))

def do_markdown(value, code=False):
    if not code:
        return markdown.markdown(value)
    return markdown.markdown(value, ['codehilite(force_linenos=True)'])

def do_sorted(value):
    return sorted(value)

def do_authors_list(value, mod):
    res, template = [], _get_template('authors', 'link.html')
    for author_id in value:
        try:
            res.append(template.render({'author': mod[author_id]}))
        except lpbm.exceptions.NoSuchAuthorError:
            pass
    return ltools.join_names(res)

class Render(lpbm.module_loader.Module):
    def name(self): return 'render'
    def abstract(self): return 'Blog generation module.'

    def init(self):
        self.needed_modules = ['authors', 'articles', 'categories']

        self.parser.add_argument('--articles', action='store_true',
                                 help='Renders all the articles.')
        self.parser.add_argument('--rss', action='store_true',
                                 help='Renders the RSS feed.')
        self.parser.add_argument('--all', action='store_true',
                                 help='Renders everything.')

    def load(self, modules, args):
        self.build_dir = tempfile.mkdtemp(prefix='lpbm_')

        # Menu header.
        menu_header = None
        menu_path = lpbm.tools.join(args.exec_path, 'menu.markdown')
        if os.path.exists(menu_path):
            with codecs.open(menu_path) as f:
                menu_header = markdown.markdown(
                    f.read().decode('utf-8')
                )

        # Jinja2 Environment Globals
        _ENV.filters.update({
            'authors_list': do_authors_list,
            'markdown': do_markdown,
            'sorted': do_sorted,
        })
        _ENV.globals.update({
            'authors_mod': self.modules['authors'],
            'categories_mod': self.modules['categories'],
            'config_mod': self.modules['config'],
            'menu_header': menu_header,
        })

    def process(self, modules, args):
        if args.articles or args.all:
            self.render_articles()

    # Functions for internal use.
    def _build_path(self, *args):
        lpbm.tools.mkdir_p(os.path.join(self.build_dir, *(args[:-1])))
        return os.path.join(self.build_dir, *args)

    def render_articles(self, draft=False):
        template = _get_template('articles', 'base.html')
        for article in self.modules['articles'].articles.values():
            if article.published == draft:
                continue
            path = self._build_path('articles', article.html_filename())
            with codecs.open(path, 'w', 'utf-8') as f:
                print('Writing article to', path)
                f.write(template.render({
                    'articles': [article],
                }))
