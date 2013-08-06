# categories.py - Category helper on command line.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Categories manager, getting authors configuration in blog sources and loading
all the categories.
'''

import sys

import lpbm.models.configmodel as cm_module
import lpbm.module_loader
import lpbm.tools as ltools

from lpbm.models.categories import Category

class Categories(lpbm.module_loader.ModelManagerModule):
    '''
    Categories manager, getting authors configuration in blog sources and
    loading all the categories.
    '''

    # pylint: disable=C0321
    def abstract(self): return 'Loads and manipulates categories.'
    def name(self): return 'categories'
    def object_name(self): return 'category'
    def object_name_plural(self): return 'categories'
    def model_cls(self): return Category

    def load(self, modules, args):
        filename = ltools.join(args.exec_path, 'categories.cfg')
        self.cm = cm_module.ConfigModel(filename)

        # Now we load all the categories.
        for section in self.cm.config.sections():
            obj = self.register_object(Category, section)

    # Manipulation function
    def recursive_view(self):
        res, cats, level = dict(), dict([(o.id, o) for o in self.objects]), 0
        while cats:
            _to_delete = []
            for cat in cats.values():
                if cat.level() == level:
                    _parent_res = res
                    for parent in cat.full_path()[:-1]:
                        _parent_res = _parent_res[parent.name][1]
                    _parent_res[cat.name] = (cat, dict())
                    _to_delete.append(cat.id)
            for it in _to_delete:
                del cats[it]
            level += 1
        return res

    def opt_new(self):
        super().opt_new(None)

    def opt_delete(self, id):
        '''Deletes an existing category.'''
        categories, to_delete = {id: self[id]}, [id]
        categories_copy = self._objects.copy()
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
            print('{level} - {name}'.format(
                name = cat.name,
                level = '  ' * (cat.level() - categories[id].level())
            ))
        if ltools.ask_sure():
            for cat in categories.values():
                cat.deleted = True
            self.cm.save()
            print('Categories successfully deleted!')
