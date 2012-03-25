# templates.py - Render the blog with templates defined here.
# Author: Franck Michea < franck,michea@gmail.com >
# License: New BSD License (See LICENSE)

import codecs
import os
import string
import subprocess

import lpbm.config
import lpbm.constants
import lpbm.menu
import lpbm.stylesheets
import lpbm.tools

def get_template(filename):
    with open(os.path.join(lpbm.constants.ROOT_TEMPLATES, filename)) as f:
        return string.Template('\n'.join(f.readlines()))

class Layout(object):
    def __init__(self, art_mgr, aut_mgr, cat_mgr):
        self.config = lpbm.config.Config()
        self.menu = lpbm.menu.Menu(cat_mgr, aut_mgr)
        self.art_mgr, self.aut_mgr, self.cat_mgr = art_mgr, aut_mgr, cat_mgr

    def set_stylesheets(self, stylesheets):
        self.stylesheets = []
        a = '<link media="screen" type="text/css" href="{}" rel="stylesheet">'
        for stl in stylesheets:
            self.stylesheets.append(a.format(
                stl.replace(lpbm.constants.ROOT_OUTPUT_STYLESHEETS, '/stylesheets')
            ))

    def output_begin(self, fd, page_title):
        # Render the header.
        fd.write(get_template('header.html').safe_substitute(
            page_title = page_title,
            title = self.config.title,
            subtitle = self.config.subtitle,
            css_files = '\n'.join(self.stylesheets),
        ))
        fd.write('<div id="main_body">\n')
        # Render the menu.
        fd.write(get_template('menu.html').safe_substitute(
            authors = self.menu.get_authors(),
            categories = self.menu.get_categories()
        ))
        fd.write('<ul id="articles">\n')

    def output_end(self, fd):
        fd.write('</ul><div class="cleaner"></div></div>\n')
        fd.write(get_template('footer.html').safe_substitute(
            footer = self.config.footer,
        ))

    def output_articles(self, filename, articles, page_title='Index'):
        f = codecs.open(os.path.join(lpbm.constants.ROOT_OUTPUT, filename),
                        'w', 'utf-8')
        self.output_begin(f, "%s: %s" % (self.config.title, page_title))
        # Render all articles.
        for article in articles:
            authors = []
            for author_login in article.authors:
                author = self.aut_mgr.authors[author_login]
                tmp = get_template('authors/profile_link.html').safe_substitute(
                    name = author.name,
                    login = author.login,
                    email = author.email,
                )
                authors.append(tmp[:-1])
            tmp = get_template('articles/body.html').safe_substitute(
                pk = article.pk,
                url = article.get_url(),
                title = article.title,
                content = article.get_content(),
                authors = ', '.join(authors),
                crt_date = article.crt_date.strftime(lpbm.constants.FRMT_DATE),
                mod_date = article.mod_date.strftime(lpbm.constants.FRMT_DATE),
            )
            f.write(tmp)
        self.output_end(f)

    def output_author(self, author):
        f = codecs.open(os.path.join(lpbm.constants.ROOT_OUTPUT, 'authors',
                        '%s.html' % author.login), 'w', 'utf-8')
        self.output_begin(f, 'Author - %s (%s)' % (author.name, author.login))
        # Render the author
        f.write(get_template('authors/body.html').safe_substitute(
            login = author.login,
            name = author.name,
            email = author.email,
            desc = author.get_description(),
        ))
        self.output_end(f)

def render(art_mgr, aut_mgr, cat_mgr):
    layout = Layout(art_mgr, aut_mgr, cat_mgr)

    lpbm.tools.mkdir_p(lpbm.constants.ROOT_OUTPUT)

    layout.set_stylesheets(lpbm.stylesheets.StylesheetsManager().stylesheets)
    layout.output_articles('index.html', art_mgr.get_articles())

    lpbm.tools.mkdir_p(os.path.join(lpbm.constants.ROOT_OUTPUT, 'articles'))

    for article in art_mgr.get_articles():
        layout.output_articles(article.get_filename(), [article],
                               ('Article - %s' % article.title))

    lpbm.tools.mkdir_p(os.path.join(lpbm.constants.ROOT_OUTPUT, 'authors'))
    for author in aut_mgr.get_authors():
        layout.output_author(author)
