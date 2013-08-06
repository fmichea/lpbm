#! /usr/bin/env python
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
This is the main file of LPBM project. You can write it either uppercased or
lowercased, I don't care. LPBM aims to provide a easy way to generate nice
prosonnal blog based on markdown files. See README and documentation for more
details.
'''

import argparse
import pdb
import sys
import traceback

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
    parser.add_argument('-b', '--backtrace', action='store_true', default=False,
                        help='print backtrace on error (default with pdb).')
    parser.add_argument('-d', '--debug', action='store_true', default=False,
                        help='print debug information.')
    parser.add_argument('-p', '--exec-path', action='store', default='.',
                        help='path where lpbm will search the blog. ' + \
                             '(default: %(default)s)')
    parser.add_argument('-P', '--pdb', action='store_true', default=False,
                        help='start pdb debugger on exception.')
    subparser = parser.add_subparsers()

    # Tools are loaded dynamically, so argument parser isn't complete.
    # pylint: disable=E1101
    lpbm.module_loader.load_modules(_MODULES, subparser)

    # Every command , we can parse command line.
    args = parser.parse_args(sys.argv[1:])

    if hasattr(args, 'func'):
        try:
            args.func(_MODULES, args)
        except Exception as err:
            if args.backtrace or args.pdb:
                traceback.print_exc()
            if args.pdb:
                pdb.post_mortem(sys.exc_info()[2])
            elif not args.backtrace:
                sys.exit('ERROR: ' + str(err))
    else:
        parser.print_help()
