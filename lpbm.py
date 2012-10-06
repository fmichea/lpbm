#! /usr/bin/env python
# render.py - Render the complete website.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
This is the main file of LPBM project. You can write it either uppercased or
lowercased, I don't care. LPBM aims to provide a easy way to generate nice
prosonnal blog based on markdown files. See README and documentation for more
details.
'''

import argparse
import sys

# pylint: disable=E0611
import lpbm.logging
import lpbm.module_loader

# FIXME: dead code
#def clean_tree():
#    # Cleaning output tree.
#    if os.path.isdir(lpbm.constants.ROOT_OUTPUT):
#        shutil.rmtree(lpbm.constants.ROOT_OUTPUT)
#    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_STYLESHEETS):
#        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_STYLESHEETS)
#    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_IMAGES):
#        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_IMAGES)
#
#def build_blog(ct_mgr, aut_mgr, art_mgr):
#    lpbm.templates.render(art_mgr, aut_mgr, cat_mgr)
#
#    if os.path.isdir(lpbm.constants.ROOT_OUTPUT_IMAGES):
#        shutil.rmtree(lpbm.constants.ROOT_OUTPUT_IMAGES)
#    os.makedirs(lpbm.constants.ROOT_OUTPUT_IMAGES)
#
#    # Copy images using os.system, like a man.
#    os.system("cp -R '%s'/* '%s'/* '%s' >/dev/null 2>&1" % (
#        lpbm.constants.ROOT_IMAGES,
#        lpbm.constants.ROOT_SRC_IMAGES,
#        lpbm.constants.ROOT_OUTPUT_IMAGES
#    ))
#
#def build_rss(cat_mgr, aut_mgr, art_mgr):
#    lpbm.rss.render(art_mgr, aut_mgr, cat_mgr)
#    pass

_MODULES = dict()

def main():
    '''Initialization of logging module and parser. Calls module_loader.'''
    # pylint: disable=E1101
    lpbm.logging.init()

    # Command line arguments.
    parser = argparse.ArgumentParser(
        description='Lightweight Personal Blog Maker'
    )
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='Prints debug information.')
    parser.add_argument('-p', '--exec-path', action='store', default='./sources',
                        help='Path where LPBM will search the blog. ' + \
                             '(default: %(default)s)')
    subparser = parser.add_subparsers()

    # Tools are loaded dynamically, so argument parser isn't complete.
    # pylint: disable=E1101
    lpbm.module_loader.load_modules(_MODULES, subparser)

    # Every command , we can parse command line.
    args = parser.parse_args(sys.argv[1:])

    args.func(_MODULES, args)

if __name__ == '__main__':
    main()

# FIXME: dead code.
#    # Doing what is asked.
#    if args.clean: clean_tree()
#
#    # Parsing articles, authors and generating categories.
#    if not args.no_blog or not args.no_rss:
#        cat_mgr = lpbm.categories.CategoryManager('Categories')
#        aut_mgr = lpbm.authors.AuthorsManager()
#        art_mgr = lpbm.articles.ArticlesManager(aut_mgr, cat_mgr)
#
#    # Generating what is asked.
#    if not args.no_blog:
#        build_blog(cat_mgr, aut_mgr, art_mgr)
#    if not args.no_rss:
#        build_rss(cat_mgr, aut_mgr, art_mgr)
