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
        group.add_argument('-d', '--delete', action='store_true',
                           help='Delete a category and all its children.')

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
            return
        elif args.new:
            self.new_category()
            return

        if args.id is None:
            self.parser.error('This action needs --id option.')
        elif args.edit:
            self.edit_category(args.id)
        elif args.delete:
            self.delete_category(args.id)

    # Manipulation function
    def _get_category(self, id):
        try:
            return self.categories[id]
        except KeyError:
            sys.exit('This category doesn\'t exist.')

    # All the actions.
    def list_categories(self, short=False):
        if not short:
            print('All categories:')
        if self.categories:
            categories = sorted(self.categories.values())
            for cat in categories:
                print('{level} {id:2d} + {name}'.format(
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

    def edit_category(self, id):
        category = self._get_category(id)
        category.interactive()
        self.cm.save()

    def delete_category(self, id):
        categories, to_delete = {id: self._get_category(id)}, [id]
        categories_copy = self.categories.copy()
        while to_delete:
            to_delete = []
            for cat_id, cat in categories_copy.items():
                if cat.parent in categories:
                    categories[cat.id] = cat
                    to_delete.append(cat.id)
            for cat_id in to_delete:
                del categories_copy[cat_id]
        print('All categories to be deleted:')
        for cat in categories.values():
            print('{level} + {name}'.format(
                name = cat.name,
                level = '  ' * (cat.level() - categories[id].level())
            ))
        if lpbm.tools.ask_sure():
            for cat in categories.values():
                self.cm.config.remove_section(str(cat.id))
            self.cm.save()
            print('Categories successfully deleted!')
