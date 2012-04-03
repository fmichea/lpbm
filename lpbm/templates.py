# templates.py - Render the blog with templates defined here.
# Author: Franck Michea < franck,michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import os
import jinja2

import lpbm.config
import lpbm.constants
import lpbm.menu
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
        })
        output_path = os.path.join(lpbm.constants.ROOT_OUTPUT, output_file)
        lpbm.tools.mkdir_p(os.path.dirname(output_path))
        f = codecs.open(output_path, 'w', 'utf-8')
        f.write(self.template.render(context))


def render(article_mgr, author_mgr, category_mgr):
    lpbm.tools.mkdir_p(lpbm.constants.ROOT_OUTPUT)
    template = Template(author_mgr, category_mgr)

    # Index, with all articles.
    template.init_template('articles', 'base.html')
    template.render('index.html', {'articles': article_mgr.get_articles()})

    # One page by article.
    article_mgr.render(template)
