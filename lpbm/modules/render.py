# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import datetime
import math
import os
import shutil
import sys
import tempfile

import PyRSS2Gen
import jinja2
import markdown

import lpbm.module_loader
import lpbm.tools as ltools

from lpbm.lib.jinja2.filters import (
    do_markdown,
    do_slugify,
    do_sorted,
)
from lpbm.lib.slugify import slugify as _slugify


_ENV = None


def _get_template(*args):
    return _ENV.get_template(os.path.join(*args))


def do_authors_list(value, mod):
    res, template = [], _get_template('authors', 'link.html')
    for author_id in value:
        try:
            res.append(template.render({'author': mod[int(author_id)]}))
        except (lpbm.exceptions.ModelDoesNotExistError, ValueError):
            pass
    return lpbm.tools.join_names(sorted(res))


class Render(lpbm.module_loader.Module):
    def name(self): return 'render'

    def abstract(self): return 'Blog generation module.'

    def init(self):
        self.needed_modules = ['authors', 'articles', 'categories']

        self.parser.add_argument('-d', '--drafts', action='store_true',
                                 default=False, help='also render drafts.')
        self.parser.add_argument('-t', '--theme', action='store',
                                 help='Try a theme to generate the blog.')
        output_help = 'change default output directory (absolute from $PWD).'
        self.parser.add_argument('-o', '--output', action='store',
                                 metavar='directory', help=output_help)
        self.parser.add_argument('-i', '--id', action='store',
                                 help='render a specific article.')
        noconfirm_help = 'do not confirm to empty output directory.'
        self.parser.add_argument('-N', '--noconfirm', action='store_true',
                                 default=False, help=noconfirm_help)

    def load(self, modules, args):
        self.build_dir = tempfile.mkdtemp(prefix='lpbm_')

        if args.output is not None:
            self.output_dir = ltools.abspath(args.output)
        else:
            self.output_dir = ltools.join(args.exec_path, 'result')

        if not os.path.exists(self.output_dir):
            msg = 'I didn\'t find directory/symbolic link named `{path}`'
            msg += ' where to put the blog.'
            sys.exit(msg.format(path=self.output_dir))

        if not args.noconfirm:
            msg = 'Are you sure you want to generate your blog in `{path}`?\n'
            msg += 'This action will remove all its contents!'
            if not ltools.ask_sure(prompt=msg.format(path=self.output_dir)):
                sys.exit('Nothing was done.')

        theme = self.modules['config']['theme.name'] or 'default'
        if args.theme is not None:
            theme = args.theme
        self.root = ltools.join(ltools.ROOT, 'themes', theme)
        if not os.path.exists(self.root):
            sys.exit('I don\'t know this theme. ({})'.format(theme))

        # Menu header.
        menu_header = None
        menu_path = lpbm.tools.join(args.exec_path, 'menu.markdown')
        if os.path.exists(menu_path):
            with codecs.open(menu_path, 'r', 'utf-8') as f:
                menu_header = markdown.markdown(f.read())

        # Jinja2 Environment Globals
        global _ENV
        _ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(
            ltools.join(self.root, 'templates')
        ))
        _ENV.filters.update({
            'authors_list': do_authors_list,
            'markdown': do_markdown,
            'slugify': do_slugify,
            'sorted': do_sorted,
        })
        categories_menu = self.modules['categories'].recursive_view()
        cats_visible = self._get_categories()

        def _categories_menu(c):
            return dict(
                (i, (cat, _categories_menu(children)))
                for i, (cat, children) in c.items()
                if cat.id in cats_visible
            )

        categories_menu = _categories_menu(categories_menu)
        _ENV.globals.update({
            'authors_mod': self.modules['authors'],
            'categories_menu': categories_menu,
            'config_mod': self.modules['config'],
            'menu_header': menu_header,
        })

    def process(self, modules, args):
        try:
            # Last update of environment before beginning of page generation,
            _ENV.globals.update({
                'static_files':  self.copy_static_files(),
            })

            self.render_articles()
            self.render_categories()
            self.render_authors()
            self.render_rss()

            # If full rendering completed (we are still alive), then we copy the
            # temporary directory to the output directory.
            self._copy_all()
        finally:
            shutil.rmtree(self.build_dir)

    # Functions for internal use.
    def _build_path(self, *args):
        lpbm.tools.mkdir_p(ltools.join(self.build_dir, *(args[:-1])))
        return ltools.join(self.build_dir, *args)

    def _get_articles(self, limit=None, filter=None):
        if self.args.id is not None:
            try:
                articles = [self.modules['articles'][int(self.args.id)]]
            except ValueError:
                raise Exception('Article id must be an int.')
        else:
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

    def _copy_static_dir(self, statics, fltr, *subdirs):
        out_root = self._build_path(*subdirs)

        def sub(root):
            res = []
            for root, filename in ltools.filter_files(fltr, root, *(subdirs[1:])):
                res.append(ltools.join('/', *(subdirs + (filename,))))
                ltools.copy(ltools.join(root, filename),
                            ltools.join(out_root, filename))
            return res

        sub(self.root)
        statics.extend(sub(ltools.join(self.args.exec_path, 'medias')))

    def copy_static_files(self):
        static_files = {'css': [], 'js': [], 'images': [], 'data': [], 'fonts': []}
        self._copy_static_dir(static_files['css'], lambda a: a.endswith('.css'),
                              'medias', 'css')
        for n in ['images', 'data', 'js', 'fonts']:
            self._copy_static_dir(static_files[n], lambda a: True, 'medias', n)
        return static_files

    # Public functions.
    def render_articles(self):
        template = _get_template('articles', 'base.html')
        for article in self._get_articles():
            path = self._build_path('articles', article.html_filename())
            with codecs.open(path, 'w', 'utf-8') as f:
                print('Writing article to', path)
                f.write(template.render({
                    'page_title': article.title,
                    'comments_enabled': True,
                    'articles': [article],
                }))
        kwds = {
            'pages_root': '/pages',
        }
        self.render_index([], self._get_articles(), **kwds)
        self.render_pages(['pages'], self._get_articles(), **kwds)

    def render_index(self, directory, articles, **kwargs):
        template = _get_template('articles', 'base.html')
        limit = self.modules['config']['paginate.nb_articles'] or 5
        articles_ = articles[:limit]
        with codecs.open(self._build_path(*(directory + ['index.html'])), 'w', 'utf-8') as f:
            print('Writing index file for {}.'.format(os.path.join('/', *directory)))
            kwargs_ = dict(kwargs)
            kwargs_.update({
                'show_more': limit < len(articles),
                'articles': articles_,
            })
            f.write(template.render(kwargs_))

    def render_pages(self, directory, articles, **kwargs):
        app = self.modules['config']['paginate.nb_articles'] or 5
        pwidth = self.modules['config']['paginate.width'] or 5
        pages = int(math.ceil(len(articles) / float(app)))

        def left_stone(page):
            return min(max(0, page - pwidth // 2), max(0, pages - pwidth))

        def right_stone(page):
            rstone = pwidth // 2 + (1 if 0 < pwidth / 2 else 0)
            return max(min(pages, page + rstone), min(pages, pwidth))

        template = _get_template('articles', 'base.html')
        display_pages = range(1, pages + 1)
        main_title = kwargs.get('page_title', None)
        if main_title:
            main_title += ' - Page {}'
        else:
            main_title = 'Page {}'
        for page in range(pages):
            display_page = page + 1
            kwargs['page_title'] = main_title.format(display_page)
            tmp = 'page-{}.html'.format(display_page)
            with codecs.open(self._build_path(*(directory + [tmp])), 'w', 'utf-8') as f:
                kwargs_ = dict(kwargs)
                kwargs_.update({
                    'articles': articles[page * app: (page + 1) * app],
                    'cur_page': display_page,
                    'last_page': pages,
                    'pages': display_pages[left_stone(page):right_stone(page)],
                    'paginate': True,
                })
                f.write(template.render(kwargs_))

    def render_rss(self):
        def rss_item(article):
            def rss_aut(author_id):
                try:
                    author = self.modules['authors'][author_id]
                    return '{email} ({full_name})'.format(
                        email=author.email,
                        full_name=author.full_name(),
                    )
                except lpbm.exceptions.ModelDoesNotExistError:
                    return '[deleted]'
            authors = ltools.join_names([rss_aut(a) for a in article.authors])
            return PyRSS2Gen.RSSItem(
                title=article.title,
                link='{base_url}articles/{html_filename}'.format(
                    base_url=self.modules['config']['general.url'],
                    html_filename=article.html_filename(),
                ),
                author=authors,
                guid=str(article.id),
                description=do_markdown(article.content, code=False),
                pubDate=article.date,
            )
        print('Generating RSS file.')
        articles = self._get_articles(self.modules['config']['rss.nb_articles'] or 10)
        rss = PyRSS2Gen.RSS2(
            title=self.modules['config']['general.title'],
            link=self.modules['config']['general.url'],
            description=self.modules['config']['general.subtitle'],
            lastBuildDate=datetime.datetime.now(),
            items=[rss_item(a) for a in articles],
        )
        rss_path = ltools.join(self.build_dir, 'rssfeed.xml')
        with codecs.open(rss_path, 'w', 'utf-8') as f:
            rss.write_xml(f, encoding='utf-8')

    def _get_categories(self):
        categories = dict()
        for article in self._get_articles():
            for cat in article.categories:
                for pcat in self.modules['categories'][cat].full_path():
                    try:
                        categories[pcat.id] |= set([article])
                    except KeyError:
                        categories[pcat.id] = set([article])
        return categories

    def render_categories(self):
        categories = self._get_categories()
        for id, articles in categories.items():
            cat = self.modules['categories'][id]
            dirs = list(os.path.split(os.path.dirname(cat.html_filename())))
            kwargs = {
                'page_title': cat.name,
                'cur_cat': cat.id,
                'pages_root': os.path.join(*(['/'] + dirs)),
            }
            self.render_index(dirs, list(articles), **kwargs)
            self.render_pages(dirs, list(articles), **kwargs)

    def render_authors(self):
        authors = dict()
        for article in self._get_articles():
            for author in article.authors:
                try:
                    authors[author] |= set([article])
                except KeyError:
                    authors[author] = set([article])
        for id, articles in authors.items():
            author = self.modules['authors'][id]
            dirs = ['authors', _slugify(author.nickname)]
            kwargs = {
                'page_title': '{} ({})'.format(author.full_name(), author.nickname),
                'cur_author': author.id,
                'pages_root': os.path.join(*(['/'] + dirs)),
            }
            self.render_index(dirs, list(articles), **kwargs)
            self.render_pages(dirs, list(articles), **kwargs)
