# lpbm/modules/authors.py - Loads and manipulates authors.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Author manager, getting authors configuration in blog sources and loading all
the authors.
'''

import sys

import lpbm.datas.authors
import lpbm.datas.configmodel as cm_module
import lpbm.logging
import lpbm.module_loader
import lpbm.path

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
                                 metavar='nickname', help='Selects an author.')

        group = self.parser.add_argument_group(title='general actions')
        group.add_argument('-l', '--list', action='store_true',
                           help='List the nicknames.')

        group = self.parser.add_argument_group(
            title='specific actions (need --id)'
        )
        group.add_argument('-n', '--new', action='store_true',
                           help='Helper to add a new author.')
        group.add_argument('-e', '--edit', action='store_true',
                           help='Helper to edit an author.')
        group.add_argument('-d', '--delete', action='store_true',
                           help='Helper to delete an author.')

    def load(self, modules, args):
        filename = lpbm.path.join(args.exec_path, 'authors.cfg')
        self.cm = cm_module.ConfigModel(filename)

        # Now loads all authors.
        for section in self.cm.config.sections():
            self.authors[section] = lpbm.datas.authors.Author(section, self.cm)

    def process(self, modules, args):
        if args.list:
            self.list_authors()
            return

        # Following options need --id precised to work.
        if args.id is None:
            self.parser.error('This action needs --id option.')
        elif args.new:
            self.new_author(args.id)
        elif args.edit:
            self.edit_author(args.id)
        elif args.delete:
            self.delete_author(args.id)

    # Particular functions requested on command line.
    def list_authors(self):
        '''This function lists all the authors of the blog.'''
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

    def new_author(self, nickname):
        '''Interactively create an author.'''
        if self.cm.config.has_section(nickname):
            sys.exit('This nickname is already used!')
        author = lpbm.datas.authors.Author(nickname, self.cm)
        try:
            author.id = max([aut.id for aut in self.authors.values()]) + 1
        except ValueError:
            author.id = 0
        author.interactive()
        self.cm.save()

    def edit_author(self, nickname):
        '''Interactively edit and existing author.'''
        if nickname not in self.authors.keys():
            sys.exit('Unknown author nickname!')
        self.authors[nickname].interactive()
        self.cm.save()

    def delete_author(self, nickname):
        '''Deletes an author from authors list.'''
        if nickname not in self.authors.keys():
            sys.exit('Unknown author nickname!')
        self.cm.config.remove_section(nickname)
        self.cm.save()
