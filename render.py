#! /usr/bin/env python2
# render.py - Render the complete website.
# Author: Franck Michea < franck.michea@gmail.com >

import argparse
import os
import shutil
import sys

import lpbm.articles
import lpbm.authors
import lpbm.categories
import lpbm.rss
import lpbm.templates

def clean_tree():
    # Cleaning output tree.
    if os.path.isdir(lpbm.constants.ROOT_OUTPUT):
        shutil.rmtree(lpbm.constants.ROOT_OUTPUT)
    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_STYLESHEETS):
        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_STYLESHEETS)
    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_IMAGES):
        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_IMAGES)

def build_blog(ct_mgr, aut_mgr, art_mgr):
    lpbm.templates.render(art_mgr, aut_mgr, cat_mgr)

    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_IMAGES):
        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_IMAGES)
    os.makedirs(lpbm.constants.ROOT_OUTPUT_IMAGES)

    # Copy images using os.system, like a man.
    os.system("cp -R '%s'/* '%s'/* '%s' >/dev/null 2>&1" % (
        lpbm.constants.ROOT_IMAGES,
        lpbm.constants.ROOT_SRC_IMAGES,
        lpbm.constants.ROOT_OUTPUT_IMAGES
    ))

def build_rss(cat_mgr, aut_mgr, art_mgr):
    lpbm.rss.render(art_mgr, aut_mgr, cat_mgr)

if __name__ == '__main__':
    # Command line arguments.
    parser = argparse.ArgumentParser(
        description='Lightweight Personal Blog Maker'
    )
    parser.add_argument('-c', '--clean', action='store_true', default=False,
                        help='Clean output tree before generation.')
    parser.add_argument('-B', '--no-blog', action='store_true', default=False,
                        help='Avoid generating blog.')
    parser.add_argument('-R', '--no-rss', action='store_true', default=False,
                        help='Avoid generating RSS.')
    args = parser.parse_args(sys.argv[1:])

    # Doing what is asked.
    if args.clean: clean_tree()

    # Parsing articles, authors and generating categories.
    if not args.no_blog or not args.no_rss:
        cat_mgr = lpbm.categories.CategoryManager('Categories')
        aut_mgr = lpbm.authors.AuthorsManager()
        art_mgr = lpbm.articles.ArticlesManager(aut_mgr, cat_mgr)

    # Generating what is asked.
    if not args.no_blog:
        build_blog(cat_mgr, aut_mgr, art_mgr)
    if not args.no_rss:
        build_rss(cat_mgr, aut_mgr, art_mgr)
