# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import PyRSS2Gen
import codecs
import datetime
import jinja2
import markdown
import math
import os
import sys
import tempfile

import lpbm.module_loader
import lpbm.tools as ltools

_ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(
    ltools.join(ltools.ROOT, 'medias', 'templates')
))

def _get_template(*args):
    return _ENV.get_template(os.path.join(*args))

# Miscenalleous filters for jinja2
def do_markdown(value, code=True):
    if not code:
        return markdown.markdown(value)
    return markdown.markdown(value, ['codehilite(force_linenos=True)'])

def do_sorted(value):
    return sorted(value)

def do_authors_list(value, mod):
    res, template = [], _get_template('authors', 'link.html')
    for author_id in value:
        try:
            res.append(template.render({'author': mod[int(author_id)]}))
        except (lpbm.exceptions.ModelDoesNotExistError, ValueError):
            pass
    return ltools.join_names(sorted(res))

class Render(lpbm.module_loader.Module):
    def name(self): return 'render'
    def abstract(self): return 'Blog generation module.'

    def init(self):
        self.needed_modules = ['authors', 'articles', 'categories']

        self.parser.add_argument('--drafts', action='store_true', default=False,
                                 help='also render drafts.')

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
            with codecs.open(menu_path, 'r', 'utf-8') as f:
                menu_header = markdown.markdown(f.read())

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

        self.render_articles()
        self.render_rss()
        self.render_categories()

        # If full rendering completed (we are still alive), then we copy the
        # temporary directory to the output directory.
        self._copy_all()

    # Functions for internal use.
    def _build_path(self, *args):
        lpbm.tools.mkdir_p(ltools.join(self.build_dir, *(args[:-1])))
        return ltools.join(self.build_dir, *args)

    def _get_articles(self, limit=None, filter=None):
        articles = sorted(self.modules['articles'].objects)
        articles = [a for a in articles if a.published or self.args.drafts]
        articles = list(reversed(articles))
        if filter is not None:
            articles = [a for a in articles if filter(a)]
        if limit is not None:
            articles = articles[:limit]
        return articles

    def _copy_all(self):
        # First big clean up of all the files.
        ltools.empty_directory(self.output_dir)
        ltools.move_content(self.build_dir, self.output_dir)
        os.rmdir(self.build_dir)

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

    # Public functions.
    def render_articles(self):
        template = _get_template('articles', 'base.html')
        for article in self._get_articles():
            path = self._build_path('articles', article.html_filename())
            with codecs.open(path, 'w', 'utf-8') as f:
                print('Writing article to', path)
                f.write(template.render({
                    'articles': [article],
                }))
        self.render_index([], self._get_articles())
        self.render_pages(['pages'], self._get_articles())

    def render_index(self, directory, articles):
        template = _get_template('articles', 'base.html')
        limit = self.modules['config']['paginate.nb_articles'] or 5
        articles_ = articles[:limit]
        with codecs.open(self._build_path(*(directory + ['index.html'])), 'w', 'utf-8') as f:
            print('Writing index file.')
            f.write(template.render({
                'show_more': limit < len(articles),
                'articles': articles_,
            }))

    def render_pages(self, directory, articles):
        app = self.modules['config']['paginate.nb_articles'] or 5
        pwidth = self.modules['config']['paginate.width'] or 5
        pages = int(math.ceil(len(articles) / float(app)))
        def left_stone(page):
            return min(max(0, page - pwidth / 2), max(0, pages - pwidth))
        def right_stone(page):
            return max(min(pages, page + pwidth / 2), min(pages, pwidth - 1))
        template = _get_template('articles', 'base.html')
        display_pages = range(1, pages + 1)
        for page in range(pages):
            display_page = page + 1
            tmp = 'page-{}.html'.format(display_page)
            with codecs.open(self._build_path(*(directory + [tmp])), 'w', 'utf-8') as f:
                f.write(template.render({
                    'articles': articles[page * app: (page + 1) * app],
                    'cur_page': display_page,
                    'last_page': pages,
                    'pages': display_pages[left_stone(page):right_stone(page)],
                    'paginate': True,
                }))

    def render_rss(self):
        def rss_item(article):
            def rss_aut(author_id):
                try:
                    author = self.modules['authors'][author_id]
                    return '{email} ({full_name})'.format(
                        email = author.email,
                        full_name = author.full_name(),
                    )
                except lpbm.exceptions.ModelDoesNotExistError:
                    return '[deleted]'
            authors = ltools.join_names([rss_aut(a) for a in article.authors])
            return PyRSS2Gen.RSSItem(
                title = article.title,
                link = '{base_url}{html_filename}'.format(
                    base_url = self.modules['config']['general.url'],
                    html_filename = article.html_filename(),
                ),
                author = authors,
                guid = str(article.id),
                description = do_markdown(article.content),
                pubDate = article.date,
            )
        print('Generating RSS file.')
        articles = self._get_articles(self.modules['config']['rss.nb_articles'] or 10)
        rss = PyRSS2Gen.RSS2(
            title = self.modules['config']['general.title'],
            link = self.modules['config']['general.url'],
            description = self.modules['config']['general.subtitle'],
            lastBuildDate = datetime.datetime.now(),
            items = [rss_item(a) for a in articles],
        )
        rss_path = ltools.join(self.build_dir, 'rssfeed.xml')
        with codecs.open(rss_path, 'w', 'utf-8') as f:
            rss.write_xml(f, encoding='utf-8')

    def render_categories(self):
        for cat in self.modules['categories'].objects:
            dirs = list(os.path.split(os.path.dirname(cat.html_filename())))
            articles = self._get_articles(filter=lambda a: cat.id in a.categories)
            self.render_pages(dirs, articles)
            self.render_index(dirs, articles)
