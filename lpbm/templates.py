# templates.py - Render the blog with templates defined here.
# Author: Franck Michea < franck,michea@gmail.com >

import os
import string
import subprocess
import codecs

import lpbm.constants
import lpbm.config
import lpbm.menu

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
                stl.replace(lpbm.constants.ROOT_MEDIA, '/media')
            ))

    def output(self, filename, articles, page_title='Index'):
        f = codecs.open(os.path.join(lpbm.constants.ROOT_OUTPUT, filename),
                        'w', 'utf-8')

        # Render the header.
        f.write(get_template('header.html').safe_substitute(
            page_title = page_title,
            title = self.config.title,
            subtitle = self.config.subtitle,
            css_files = '\n'.join(self.stylesheets),
        ))

        f.write('<div id="main_body">\n')

        # Render the menu.
        f.write(get_template('menu.html').safe_substitute(
            authors = self.menu.get_authors(),
            categories = self.menu.get_categories()
        ))

        f.write('<ul id="articles">\n')

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
                content = article.get_content(),
                authors = ', '.join(authors),
                crt_date = article.crt_date.strftime(lpbm.constants.FRMT_DATE),
                mod_date = article.mod_date.strftime(lpbm.constants.FRMT_DATE),
            )
            f.write(tmp)

        f.write('</ul><div class="cleaner"></div></div>\n')
        f.write(get_template('footer.html').safe_substitute(
            footer = self.config.footer,
        ))

def render_stylesheets():
    res = []

    for root, dirs, files in os.walk(lpbm.constants.ROOT_STYLESHEETS):
        for filename in files:
            if not filename.endswith('.scss'):
                continue
            out_path = os.path.join(root, (filename[:-5] + '.css'))
            f = open(out_path, 'w')
            path = os.path.join(root, filename)
            p = subprocess.Popen(['sass', path], stdout=subprocess.PIPE)
            out, err = p.communicate()
            if p.returncode == 0:
                res.append(out_path)
                f.write(out)
            f.close()

    # Pygments stylesheet.
    path = os.path.join(lpbm.constants.ROOT_STYLESHEETS, 'pygments.css')
    subprocess.call('pygmentize -S default -f html > %s' % path, shell=True)
    res.append(path)

    return res

def create_dir_absent(path):
    if not os.path.isdir(path):
        os.mkdir(path, 0755)

def render(art_mgr, aut_mgr, cat_mgr):
    layout = Layout(art_mgr, aut_mgr, cat_mgr)

    create_dir_absent(lpbm.constants.ROOT_OUTPUT)

    layout.set_stylesheets(render_stylesheets())
    layout.output('index.html', art_mgr.get_articles())

    create_dir_absent(os.path.join(lpbm.constants.ROOT_OUTPUT, 'articles'))

    for article in art_mgr.get_articles():
        layout.output(os.path.join('articles', '%d.html' % article.pk),
                      [article], ('Article - %s' % article.title))
