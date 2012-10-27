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
