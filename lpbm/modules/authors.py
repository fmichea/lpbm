# lpbm/modules/authors.py - Loads and manipulates authors.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import configparser
import sys

import lpbm.authors
import lpbm.logging
import lpbm.module_loader
import lpbm.path

class Authors(lpbm.module_loader.Module):
    def name(self): return 'authors'
    def abstract(self): return 'Loads, manipulates and renders authors.'

    def init(self):
        self.authors = dict()

        self.parser.add_argument('-l', '--list', action='store_true',
                                 help='List the nicknames.')
        self.parser.add_argument('-n', '--new', action='store', metavar='nickname',
                                 help='Helper to add a new author.')
        self.parser.add_argument('-e', '--edit', action='store', metavar='nickname',
                                 help='Helper to edit an author.')

    def load(self, modules, args):
        self.config = configparser.ConfigParser()
        self.filename = lpbm.path.join(args.exec_path, 'authors.cfg')
        try:
            with open(self.filename, 'r') as f:
                self.config.read_file(f)
        except IOError:
            return

        # Now loads all authors.
        for section in self.config.sections():
            self.authors[section] = lpbm.authors.Author(section, self.config)

    def process(self, modules, args):
        if args.list:
            self.list_authors()
        elif args.new:
            self.new_author(args.new)
        elif args.edit:
            self.edit_author(args.edit)

    def save(self):
        with open(self.filename, 'w') as f:
            self.config.write(f)

    # Particular functions requested on command line.
    def list_authors(self):
        print('All authors:')
        if self.authors:
            for key, author in sorted(self.authors.items()):
                email = '[{}]'.format(author.email) if author.email else ''
                print(' + {first} {last} a.k.a. {nickname} {email}'.format(
                    nickname = author.nickname,
                    first = author.first_name,
                    last = author.last_name,
                    email = email
                ))
        else:
            print(' + There is no author.')

    def new_author(self, nickname):
        if self.config.has_section(nickname):
            sys.exit('This nickname is already used!')
        author = lpbm.authors.Author(nickname, self.config)
        author.interactive()
        self.save()

    def edit_author(self, nickname):
        if nickname not in self.authors.keys():
            sys.exit('Unknown author nickname!')
        self.authors[nickname].interactive()
        self.save()
