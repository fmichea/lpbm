# lpbm/modules/config.py - Loads and sets configuration.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Configuration can be manipulated with this module, so that use should never
have to change the file by hand.
'''

import configparser
import os
import sys

import lpbm.logging
import lpbm.module_loader
import lpbm.tools as ltools
from lpbm.lib.deprecated_command import deprecated_command

_CONFIGURATION = {
    # 'sectionName': (Required, {
    #    'optionName': (Required, Description),
    # }),
    'general': (True, {
        'url': (True, 'Base url of the blog (ex: http://blog.example.com/).'),
        'title': (True, 'Title of the blog.'),
        'subtitle': (False, 'Sub-title of the blog.'),
        'footer': (False, 'Footer of the blog. (default: RSS link).'),
    }),
    'theme': (False, {
        'name': (False, 'Name of the theme you want to use (default, bootstrap).'),
    }),
    'paginate': (False, {
        'width': (False, 'Width of the slice for page selection (default: 5).'),
        'nb_articles': (False, 'Number of articles per page. (default: 5).'),
    }),
    'rss': (False, {
        'nb_articles': (False, 'Number of articles in RSS Feed. (default: 10).'),
    }),
    'social': (False, {
        'twitter_id': (False, 'Twitter id, for the mention (ex: kushou_)'),
        'disqus_id': (False, 'Disqus id for comments in articles.'),
    }),
    'logging-std': (False, {
        'level': (False, 'Level of messages logged on stderr.'),
    }),
}


class Config(lpbm.module_loader.Module):
    '''
    Configuration can be manipulated with this module, so that use should never
    have to change the file by hand.
    '''

    def name(self): return 'config'

    def abstract(self): return 'Manipulates blog configuration.'

    def init(self):
        self.parser.add_argument('-l', '--list', action='store_true',
                                 help='List available options, with their meaning.')
        _help = 'Check syntax and options of the configuration file.'
        self.parser.add_argument('-k', '--check', action='store_true', help=_help)
        self.parser.add_argument('-s', '--set', action='store', metavar='option',
                                 help='Set option to value (section.option=val).')
        self.parser.add_argument('-u', '--unset', action='store', metavar='option',
                                 help='Unset an option (section.option).')

    def process(self, modules, args):
        # We must show all available options.
        if args.list:
            self.list_options()
        # Check if the file is of the good format.
        elif args.check:
            self.check_options()
        # We must set the variable.
        elif args.set:
            self.set_var(args.set)
        # We want to unset some variable.
        elif args.unset:
            self.unset_var(args.unset)
        else:
            self.parser.print_help()

        try:
            with open(ltools.join(args.exec_path, 'lpbm.cfg'), 'w') as f:
                self.config.write(f)
        except IOError:
            pass

    def load(self, modules, args):
        config_path = ltools.join(args.exec_path, 'lpbm.cfg')

        if not os.path.exists(config_path):
            sys.exit('This execution path ({}) doesn\'t look like an LPBM'
                     ' blog.'.format(args.exec_path))

        self.config = configparser.ConfigParser()
        self.config.read(config_path)

        # Getting logging related configurations
        logging_conf = dict()
        for section in self.config.sections():
            if not section.startswith('logging'):
                continue
            logging_conf[section] = dict()
            for option in self.config[section]:
                logging_conf[section][option] = self.config[section][option]
        if args.debug:
            logging_conf.update({'logging-std': {'level': 'DEBUG'}})
        lpbm.logging.configure(logging_conf)

    # Access to the configuration safely.
    def __getitem__(self, name):
        try:
            section, option = name.split('.')
        except ValueError:
            return None
        return self.config.get(section, option, fallback=None)

    # Particular functions for configuration.
    def list_options(self):
        """
        List all the available options with an abstract of their meaning.
        """
        deprecated_command()

    def check_options(self):
        """
        Display all the detected options, the one missing and finally the one
        in the configuration file that wasn't detected (to warn for typos
        etc...).
        """
        deprecated_command()

    def set_var(self, var):
        """Set a variable in the configuration and saves the configuration."""
        deprecated_command()

    def unset_var(self, var):
        """
        Unset a variable in the configuration and saves the configuration. It
        checks that the variable can safely be unsafe.
        """
        deprecated_command()
