# categories.py - Category helper on command line.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Categories manager, getting authors configuration in blog sources and loading
all the categories.
'''

import lpbm.models.configmodel as cm_module
import lpbm.module_loader
import lpbm.tools as ltools
from lpbm.lib.deprecated_command import deprecated_command
from lpbm.models.categories import Category


class Categories(lpbm.module_loader.ModelManagerModule):
    '''
    Categories manager, getting authors configuration in blog sources and
    loading all the categories.
    '''

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
            self.register_object(Category, section)

    def opt_new(self):
        super().opt_new(None)

    def opt_delete(self, id):
        '''Deletes an existing category.'''
        deprecated_command()
