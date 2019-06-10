# lpbm/modules/authors.py - Loads and manipulates authors.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Author manager, getting authors configuration in blog sources and loading all
the authors.
'''

import lpbm.exceptions
import lpbm.logging
import lpbm.models.configmodel as cm_module
import lpbm.module_loader
import lpbm.tools as ltools
from lpbm.models.authors import Author


class Authors(lpbm.module_loader.ModelManagerModule):
    '''
    Author manager, getting authors configuration in blog sources and loading
    all the authors.
    '''

    def abstract(self): return 'Loads, manipulates and renders authors.'

    def model_cls(self): return Author

    def name(self): return 'authors'

    def object_name(self): return 'author'

    def init(self):
        super().init()

    def load(self, modules, args):
        filename = ltools.join(args.exec_path, 'authors.cfg')
        self.cm = cm_module.ConfigModel(filename)

        # Now loads all authors.
        for section in self.cm.config.sections():
            self.register_object(Author, section)

    # Particular functions requested on command line.
    def opt_new(self):
        '''Interactively create an author.'''
        super().opt_new(None)
