# lpbm/modules/authors.py - Loads and manipulates authors.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Author manager, getting authors configuration in blog sources and loading all
the authors.
'''

import os
import sys

import lpbm.datas.authors
import lpbm.datas.configmodel as cm_module
import lpbm.exceptions
import lpbm.logging
import lpbm.module_loader
import lpbm.tools as ltools

class Authors(lpbm.module_loader.Module):
    '''
    Author manager, getting authors configuration in blog sources and loading
    all the authors.
    '''

    # pylint: disable=C0321
    def name(self): return 'authors'
    def abstract(self): return 'Loads, manipulates and renders authors.'

    def init(self):
        self.authors = dict()

        self.parser.add_argument('-i', '--id', action='store',
                                 metavar='id', help='Selects an author.')

        group = self.parser.add_argument_group(title='general actions')
        group.add_argument('-l', '--list', action='store_true',
                           help='List the nicknames.')
        group.add_argument('-n', '--new', action='store_true',
                           help='Helper to add a new author.')

        group = self.parser.add_argument_group(
            title='specific actions (need --id)'
        )
        group.add_argument('-e', '--edit', action='store_true',
                           help='Helper to edit an author.')
        group.add_argument('-d', '--delete', action='store_true',
                           help='Helper to delete an author.')

    def load(self, modules, args):
        filename = ltools.join(args.exec_path, 'authors.cfg')
        self.cm = cm_module.ConfigModel(filename)

        # Now loads all authors.
        for section in self.cm.config.sections():
             author = lpbm.datas.authors.Author(section, self.cm)
             self.authors[author.id] = author

    def process(self, modules, args):
        if args.list:
            self.list_authors()
            return
        elif args.new:
            self.new_author()
            return

        # Following options need --id precised to work.
        if args.id is None:
            self.parser.error('This action needs --id option.')
        elif args.edit:
            self.edit_author(args.id)
        elif args.delete:
            self.delete_author(args.id)

    # Random module functions internal to lpbm
    def __getitem__(self, idx):
        try:
            return self.authors[int(idx)]
        except KeyError:
            raise lpbm.exceptions.NoSuchAuthorError(idx)

    def is_valid(self, authors):
        authors = ltools.split_on_comma(authors)
        try:
            authors = [int(idx) for idx in authors]
        except ValueError:
            return False
        for author in authors:
            if author not in self.authors:
                print('Author id {} is invalid!'.format(author))
                return False
        return True

    # Particular functions requested on command line.
    def list_authors(self, short=False):
        '''This function lists all the authors of the blog.'''
        if not short:
            print('All authors:')
        if self.authors:
            for _, author in sorted(self.authors.items()):
                email = ' [{}]'.format(author.email) if author.email else ''
                print(' {id:2d} + {first} {last} a.k.a. {nickname}{email}'.format(
                    id = author.id,
                    nickname = author.nickname,
                    first = author.first_name,
                    last = author.last_name,
                    email = email
                ))
        else:
            print(' + There is no author.')

    def new_author(self):
        '''Interactively create an author.'''
        author = lpbm.datas.authors.Author(None, self.cm)
        author.interactive()
        try:
            author.id = max(self.authors) + 1
        except ValueError:
            author.id = 0
        self.cm.save()

    def edit_author(self, id):
        '''Interactively edit and existing author.'''
        self[id].interactive()
        self.cm.save()

    def delete_author(self, id):
        '''Deletes an author from authors list.'''
        author = self[id]
        self.cm.config.remove_section(author.nickname)
        self.cm.save()
