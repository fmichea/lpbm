#! /usr/bin/python2
# render.py - Render the complete website.
# Author: Franck Michea < franck.michea@gmail.com >

import argparse
import os
import shutil
import sys

import lpbm.articles
import lpbm.authors
import lpbm.categories
import lpbm.templates

def clean_tree():
    # Cleaning output tree.
    if os.path.isdir(lpbm.constants.ROOT_OUTPUT):
        shutil.rmtree(lpbm.constants.ROOT_OUTPUT)
    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_STYLESHEETS):
        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_STYLESHEETS)

def build_blog():
    cat_mgr = lpbm.categories.CategoryManager('Categories')
    aut_mgr = lpbm.authors.AuthorsManager()
    art_mgr = lpbm.articles.ArticlesManager(aut_mgr, cat_mgr)
    lpbm.templates.render(art_mgr, aut_mgr, cat_mgr)

if __name__ == '__main__':
    # Command line arguments.
    parser = argparse.ArgumentParser(
        description='Lightweight Personal Blog Maker'
    )
    parser.add_argument('-c', '--clean', action='store_true', default=False,
                        help='Clean output tree before generation.')
    parser.add_argument('-n', '--no-blog', action='store_true', default=False,
                        help='Avoid generating blog.')
    args = parser.parse_args(sys.argv[1:])

    # Doing what is asked.
    if args.clean: clean_tree()
    if not args.no_blog: build_blog()
