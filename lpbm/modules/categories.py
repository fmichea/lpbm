# categories.py - Category helper on command line.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import lpbm.datas.categories as cd_module
import lpbm.datas.configmodel as cm_module
import lpbm.module_loader

class Categories(lpbm.module_loader.Module):
    def name(self): return 'categories'
    def abstract(self): return 'Loads and manipulates categories.'

    def init(self):
        self.categories = dict()

        self.parser.add_argument('-i', '--id', action='store', metavar='id',
                                 type=int, default=None,
                                 help='Selects a category (used by actions).')

        group = self.parser.add_argument_group(title='general actions')
        group.add_argument('-n', '--new', action='store_true',
                           help='Interactively create a category.')
        group.add_argument('-l', '--list', action='store_true',
                           help='List all the categories. (as a tree)')

        group = self.parser.add_argument_group(
            title='specific actions (need --id).'
        )
        group.add_argument('-e', '--edit', action='store_true',
                           help='Edit a category.')

    def load(self, modules, args):
        filename = lpbm.path.join(args.exec_path, 'categories.cfg')
        self.cm = cm_module.ConfigModel(filename)

        # Now we load all the categories.
        for section in self.cm.config.sections():
            id = int(section)
            self.categories[id] = cd_module.Category(self, id)

    def process(self, modules, args):
        if args.list:
            self.list_categories()
        elif args.new:
            self.new_category()

    # All the actions.
    def list_categories(self, short=False):
        if not short:
            print('All categories:')
        if self.categories:
            categories = sorted(self.categories.values())
            for cat in categories:
                print('{level} {id} + {name}'.format(
                    level = '  ' * cat.level(),
                    id = cat.id,
                    name = cat.name,
                ))
        else:
            print(' + There is no category yet.')

    def new_category(self):
        try:
            id = max([cat.id for cat in self.categories.values()]) + 1
        except ValueError:
            id = 0
        cat = cd_module.Category(self, id)
        cat.interactive()
        self.cm.save()
