import codecs
import datetime
import os
import shutil
import sys
import tempfile

import PyRSS2Gen
import jinja2

import lpbm
import lpbm.tools as ltools

_ENV = None


def _get_template(*args):
    return _ENV.get_template(os.path.join(*args))


class Migrate(lpbm.module_loader.Module):
    def name(self): return 'migrate'

    def abstract(self): return 'Migrate blog to jekyll configuration'

    def init(self):
        self.needed_modules = ['authors', 'articles', 'categories']

        output_help = 'change default output directory (absolute from $PWD).'
        self.parser.add_argument('-o', '--output', action='store',
                                 metavar='directory', help=output_help)
        noconfirm_help = 'do not confirm to empty output directory.'
        self.parser.add_argument('-N', '--noconfirm', action='store_true',
                                 default=False, help=noconfirm_help)

    def load(self, modules, args):
        self.build_dir = tempfile.mkdtemp(prefix='lpbm_jekyll_')

        if args.output is not None:
            self.output_dir = ltools.abspath(args.output)
        else:
            self.output_dir = ltools.join(args.exec_path, 'result-jekyll')

        if not os.path.exists(self.output_dir):
            msg = 'I didn\'t find directory/symbolic link named `{path}`'
            msg += ' where to put the blog.'
            sys.exit(msg.format(path=self.output_dir))

        msg = '''\
By converting your LPBM blog to Jekyll, you understand that the result will look different and some
features will be unavailable. There is also no guarantee that all links will redirect properly,
and that this is best effort.

Among the things known to break:
   - Categories are flat in Jekyll, previous categories pages (up to 10 pages) will redirect to
     one shared page.
   - Disqus comments will require manual migration (see CSV printed below).
   - RSS will be replaced with a link to new RSS feed.

Before replacing the contents of your current blog with the jekyll contents, please go through the
generation steps and check every article to ensure it is to your liking.

More at: https://jekyllrb.com/docs/

However, in exchange you get Jekyll's support, which is much better than this abandoned piece of software.
'''

        print(msg)

        if not args.noconfirm:
            msg = 'Are you sure you want to convert your blog in `{path}`?\n'
            msg += 'This action will remove all its contents!'
            if not ltools.ask_sure(prompt=msg.format(path=self.output_dir)):
                sys.exit('Nothing was done.')

        if self.modules['config']['social.disqus_id']:
            base_url = self.modules['config']['general.url']

            print('Please manually migrate the following URLs in the disqus interface:')
            print("----------------------")
            for article in self._get_articles(False):
                print(base_url.rstrip('/') + article.url() + ':' + base_url + article.jekyll_url())
            print("----------------------")

        self.simplified_article_links = True  # FIXME: remove category from article links.

        self.root = ltools.join(ltools.ROOT, 'themes', 'jekyll')

        # Jinja2 Environment Globals
        global _ENV
        _ENV = jinja2.Environment(loader=jinja2.FileSystemLoader(
            ltools.join(self.root, 'templates')
        ))
        _ENV.globals.update({
            'authors_mod': self.modules['authors'],
            'categories_mod': self.modules['categories'],
            'config_mod': self.modules['config'],
        })

    def process(self, modules, args):
        try:
            self.copy_base_structure()

            self.render_config()
            self.render_articles()
            self.render_authors()
            self.render_categories()
            self.render_rss()

            self.copy_media_files()

            # If full rendering completed (we are still alive), then we copy the
            # temporary directory to the output directory.
            self._copy_all()
        finally:
            shutil.rmtree(self.build_dir)

    def copy_base_structure(self):
        ltools.copy_content(ltools.join(self.root, 'base'), self.build_dir)

    def render_articles(self):
        template = _get_template('articles.md')

        articles_by_category = {
            '_posts': self._get_articles(False),
            '_drafts': self._get_articles(True),
        }
        for dirname, articles in articles_by_category.items():
            for article in articles:
                path = self._build_path(dirname, article.jekyll_markdown_filename())
                with codecs.open(path, 'w', 'utf-8') as f:
                    f.write(template.render({
                        'article': article,
                    }))

    def render_authors(self):
        template = _get_template('authors.md')

        for author in self.modules['authors'].objects:
            path = self._build_path('_authors', author.jekyll_markdown_filename())
            with codecs.open(path, 'w', 'utf-8') as f:
                f.write(template.render({
                    'author': author,
                }))

    def render_categories(self):
        categories = [obj.url()[:-len('/index.html')] for obj in self.modules['categories'].objects]
        with codecs.open(self._build_path('categories.md'), 'w', 'utf-8') as f:
            f.write(_get_template('categories.md').render({
                'categories': categories,
            }))

    def render_rss(self):
        link = '{base_url}/feed.xml'.format(
            base_url=self.modules['config']['general.url'].rstrip('/'),
        )

        contents = (
           '<p>This blog has been migrated to Jekyll, please find the new RSS link here: ' +
           '<a href="{l}">{l}</a></p>'
        )

        item = PyRSS2Gen.RSSItem(
            title='RSS URI changed - migration to Jekyll',
            link=link,
            guid='6D9CAD12-86D5-46D4-93F4-71C342F4B929',
            description=contents.format(l=link),
        )

        rss = PyRSS2Gen.RSS2(
            title=self.modules['config']['general.title'],
            link=self.modules['config']['general.url'],
            description=self.modules['config']['general.subtitle'],
            lastBuildDate=datetime.datetime.now(),
            items=[item],
        )

        rss_path = ltools.join(self.build_dir, 'rssfeed.xml')
        with codecs.open(rss_path, 'w', 'utf-8') as f:
            rss.write_xml(f, encoding='utf-8')

    def copy_media_files(self):
        source = ltools.join(self.args.exec_path, 'medias')
        target = ltools.join(self.build_dir, 'medias')

        if not os.path.exists(source):
            return

        ltools.copy_content(source, target)

    def render_config(self):
        path = self._build_path('_config.yml')
        with codecs.open(path, 'w', 'utf-8') as f:
            f.write(_get_template('_config.yml').render({
                'simplified_article_links': self.simplified_article_links,
            }))

    def _build_path(self, *args):
        lpbm.tools.mkdir_p(ltools.join(self.build_dir, *(args[:-1])))
        return ltools.join(self.build_dir, *args)

    def _copy_all(self):
        # First big clean up of all the files.
        ltools.empty_directory(self.output_dir)
        ltools.move_content(self.build_dir, self.output_dir)

    def _get_articles(self, drafts, limit=None, filter=None):
        articles = sorted(self.modules['articles'].objects)
        articles = [a for a in articles if a.published == (not drafts)]

        if filter is not None:
            articles = [a for a in articles if filter(a)]
        if limit is not None:
            articles = articles[:limit]
        return articles
