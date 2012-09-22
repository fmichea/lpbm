# lpbm/modules/config.py - Loads and sets configuration.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import configparser
import os
import sys

import lpbm.module_loader
import lpbm.logging

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
    'rss': (False, {
        'nb_articles': (False, 'Number of articles in RSS Feed. (default: 10).'),
    }),
    'social': (False, {
        'twitter': (False, 'Twitter id, for the mention (ex: kushou_)'),
        'disqus': (False, 'Disqus id for comments in articles.'),
    }),
    'logging-std': (False, {
        'level': (False, 'Level of messages logged on stderr.'),
    }),
}

class Config(lpbm.module_loader.Module):
    def name(self): return 'config'
    def abstract(self): return 'Manipulates blog configuration.'

    def init(self):
        self.parser.add_argument('-l', '--list', action='store_true',
                                 help='List available options, with their meaning.')
        self.parser.add_argument('-k', '--check', action='store_true',
                                 help='Check syntax and options of the configuration file.')
        self.parser.add_argument('-s', '--set', action='store', metavar='option',
                                 help='Set option to value (section.option=val).')
        self.parser.add_argument('-u', '--unset', action='store', metavar='option',
                                 help='Unset an option (section.option).')

    def process(self, modules, args):
        if args.list: # We must show all available options.
            self.list_options()
        elif args.check: # Check if the file is of the good format.
            self.check_options()
        elif args.set: # We must set the variable.
            self.set_var(args.set)
        elif args.unset: # We want to unset some variable.
            self.unset_var(args.unset)
        try:
            with open(os.path.join(args.exec_path, 'config'), 'w') as f:
                self.config.write(f)
        except IOError:
            pass

    def load(self, modules, args):
        self.config = configparser.ConfigParser()
        self.config.read(os.path.join(args.exec_path, 'config'))

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

    # Particular functions for configuration.
    def list_options(self):
        """
        List all the avilable options with an abstract of their meaning.
        """
        print('List of all options available:\n')
        for section in sorted(_CONFIGURATION.keys()):
            required, options = _CONFIGURATION[section]
            print('Section: {section} - Required: {required}'.format(
                section = section, required = required
            ))
            for option in sorted(options.keys()):
                required, desc = options[option]
                print('  ' + '+' * 70)
                print('  + Option: {}'.format(option))
                print('  + Required: {}'.format(required))
                print('  + Description: {}'.format(desc))
            print('')

    def check_options(self):
        """
        Display all the detected options, the one missing and finally the one
        in the configuration file that wasn't detected (to warn for typos
        etc...).
        """
        tmp_file = dict()
        for section in self.config.sections():
            tmp_file[section] = list(self.config[section])

        print('Checking of all the options available:')
        for section in _CONFIGURATION.keys():
            required, options = _CONFIGURATION[section]
            if section in tmp_file:
                print(' + Checking section {}'.format(section))
                for option in options:
                    required, desc = options[option]
                    try:
                        idx = tmp_file[section].index(option)
                        print('  + Option `{}` was found.'.format(option))
                        del tmp_file[section][idx]
                    except (ValueError,KeyError):
                        if required:
                            print('  ! Option `{}` is required and wasn\'t found.'.format(
                                option
                            ))
                if tmp_file[section] == []:
                    del tmp_file[section]
            elif required:
                if required:
                    print(' ! Section `{}` is required and wasn\'t found.'.format(
                        section
                    ))

        if tmp_file != dict():
            print('\nThese options are defined but not known:')
            for section in tmp_file.keys():
                print(' - Section `{}`.'.format(section))
                for option in tmp_file[section]:
                    print('  - Option `{}`.'.format(option))

    def set_var(self, var):
        """Set a variable in the configuration and saves the configuration."""
        parts = var.split('=')
        parts_ = parts[0].split('.')
        if len(parts) != 2 or len(parts_) != 2:
            print('Must set a variable. Syntax is `section.var=value`.',
                  file=sys.stderr)
            return
        section_name, var_name, value = parts_[0], parts_[1], parts[1]
        if section_name not in _CONFIGURATION:
            print('Unknown section name `{}` in configuration.'.format(section_name),
                  file=sys.stderr)
            return
        if var_name not in _CONFIGURATION[section_name][1]:
            print('Unknown variable name `{}` in section `{}` in configuration.'
                  .format(var_name, section_name), file=sys.stderr)
            return
        if value == '':
            print('You can\'t set value to empty. Use --unset to unset a variable.',
                  file=sys.stderr)
            return
        self.config[section_name][var_name] = value

    def unset_var(self, var):
        """
        Unset a variable in the configuration and saves the configuration. It
        checks that the variable can safely be unsafe.
        """
        parts = var.split('.')
        if len(parts) != 2:
            print('Syntax is `section.var`.', file=sys.stderr)
            return
        section_name, var_name = parts[0], parts[1]
        if section_name not in self.config:
            print('Section `{}` was not found in configuration.'.format(section_name),
                  file=sys.stderr)
            return
        if var_name not in self.config[section_name]:
            print('Option `{}` was not found in section `{}`.'
                  .format(var_name, section_name), file=sys.stderr)
            return
        if _CONFIGURATION[section_name][1][var_name][0]:
            print('Can\'t unset `{}` variable, it is mandatory.'.format(var),
                  file=sys.stderr)
            return
        del self.config[section_name][var_name]
        if len(self.config[section_name]) == 0:
            del self.config[section_name]
