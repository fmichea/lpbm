#! /usr/bin/python2
# render.py - Render the complete website.
# Author: Franck Michea < franck.michea@gmail.com >

import lpbm.articles
import lpbm.authors

def main():
    aut_mgr = lpbm.authors.AuthorsManager()
    art_mgr = lpbm.articles.ArticlesManager(aut_mgr)

if __name__ == '__main__':
    main()
