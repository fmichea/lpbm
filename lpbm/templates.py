# templates.py - Render the blog with templates defined here.
# Author: Franck Michea < franck,michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import jinja2
import os
import markdown

import lpbm.config
import lpbm.constants
import lpbm.paginate
import lpbm.stylesheets
import lpbm.tools


class Template(object):
    def __init__(self, author_mgr, category_mgr):
        self.template = None
        self.author_mgr = author_mgr
        self.category_mgr = category_mgr
        self.config = lpbm.config.Config()
        self.stylesheet_mgr = lpbm.stylesheets.StylesheetsManager()
        self.env = jinja2.Environment(loader=jinja2.FileSystemLoader(
            lpbm.constants.ROOT_TEMPLATES
        ))

        # Menu header (optionnal)
        menu_file = os.path.join(lpbm.constants.ROOT_SOURCES, 'menu.markdown')
        if os.path.isfile(menu_file):
            f = codecs.open(menu_file, 'r', 'utf-8')
            self.menu_header = markdown.markdown(f.read())
        else: self.menu_header = None

    def init_template(self, *template):
        self.template = self.env.get_template(os.path.join(*template))

    def render(self, output_file, context):
        if self.template is None:
            return

        context.update({
            'config': self.config,
            'author_mgr': self.author_mgr,
            'category_mgr': self.category_mgr,
            'stylesheet_mgr': self.stylesheet_mgr,
            'menu_header': self.menu_header,
        })
        output_path = os.path.join(lpbm.constants.ROOT_OUTPUT, output_file)
        lpbm.tools.mkdir_p(os.path.dirname(output_path))
        f = codecs.open(output_path, 'w', 'utf-8')
        f.write(self.template.render(context))


def render(article_mgr, author_mgr, category_mgr):
    lpbm.tools.mkdir_p(lpbm.constants.ROOT_OUTPUT)
    template = Template(author_mgr, category_mgr)

    # One page by article.
    article_mgr.render(template)

    # Paginate
    lpbm.paginate.Paginate(template, article_mgr).render()

    # Index is actually first page.
    try: os.symlink(os.path.join(lpbm.constants.ROOT_OUTPUT, 'pages/1.html'),
                    os.path.join(lpbm.constants.ROOT_OUTPUT, 'index.html'))
    except OSError: pass
