# templates.py - Render the blog with templates defined here.
# Author: Franck Michea < franck,michea@gmail.com >

import markdown
import os
import string

import lpbm.constants

def get_template(filename):
    with open(os.path.join(lpbm.constants.ROOT_TEMPLATES, filename)) as f:
        return string.Template('\n'.join(f.readlines()))

def render_main_page(art_mgr, aut_mgr, cat_mgr):
    f = open(os.path.join(lpbm.constants.ROOT_OUTPUT, 'index.html'), 'w')

    # Render all articles.
    for article in art_mgr.get_articles():
        authors = []
        for author_login in article.authors:
            author = aut_mgr.authors[author_login]
            tmp = get_template('authors/profile_link.html').safe_substitute(
                name = author.name,
                login = author.login,
                email = author.email,
            )
            authors.append(tmp[:-1])

        tmp = get_template('articles/body.html').safe_substitute(
            pk = article.pk,
            content = str(markdown.markdown(article.content)),
            authors = ', '.join(authors),
            crt_date = article.crt_date.strftime(lpbm.constants.FRMT_DATE),
            mod_date = article.mod_date.strftime(lpbm.constants.FRMT_DATE),
        )
        f.write(tmp)

    f.close()

def render(art_mgr, aut_mgr, cat_mgr):
    render_main_page(art_mgr, aut_mgr, cat_mgr)
