# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import jinja2
import markdown
import os
import tempfile
import sys

import lpbm.module_loader
import lpbm.tools as ltools

_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(
    ltools.join(ltools.ROOT, 'medias', 'templates')
))

def _get_template(*args):
    return _ENV.get_template(os.path.join(*args))

# Miscenalleous filters for jinja2
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
        self.output_dir = ltools.join(args.exec_path, 'result')

        if not os.path.exists(self.output_dir):
            sys.exit('I didn\'t find directory/symbolic link named `result`'
                     ' where to put the blog.')

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
        # Last update of environment before beginning of page generation,
        _ENV.globals.update({
            'static_files':  self.copy_static_files(),
        })

        if args.articles or args.all:
            self.render_articles()

        # If full rendering completed (we are still alive), then we copy the
        # temporary directory to the output directory.
        self._copy_all()

    # Functions for internal use.
    def _build_path(self, *args):
        lpbm.tools.mkdir_p(ltools.join(self.build_dir, *(args[:-1])))
        return ltools.join(self.build_dir, *args)

    def _copy_all(self):
        # First big clean up of all the files.
        ltools.empty_directory(self.output_dir)
        ltools.move_content(self.build_dir, self.output_dir)
        os.rmdir(self.build_dir)

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

    def _copy_static_dir(self, statics, fltr, *subdirs):
        out_root = self._build_path(*subdirs)
        def sub(root):
            res = []
            for root, filename in ltools.filter_files(fltr, root, *subdirs):
                res.append(ltools.join('/', *(subdirs + (filename,))))
                ltools.copy(ltools.join(root, filename),
                            ltools.join(out_root, filename))
            return res
        statics.extend(sub(ltools.ROOT))
        statics.extend(sub(self.args.exec_path))

    def copy_static_files(self):
        static_files = {'css': []}
        self._copy_static_dir(static_files['css'], lambda a: a.endswith('.css'),
                              'medias', 'css')
        return static_files
