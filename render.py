#! /usr/bin/python2
# render.py - Render the complete website.
# Author: Franck Michea < franck.michea@gmail.com >

import lpbm.articles
import lpbm.authors
import lpbm.categories
import lpbm.templates

def main():
    cat_mgr = lpbm.categories.CategoryManager('Categories')
    aut_mgr = lpbm.authors.AuthorsManager()
    art_mgr = lpbm.articles.ArticlesManager(aut_mgr, cat_mgr)
    lpbm.templates.render(art_mgr, aut_mgr, cat_mgr)

if __name__ == '__main__':
    main()
