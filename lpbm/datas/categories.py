# lpbm/datas/categories.py - Category model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Category's model in blog sources. Maps a section in an ini file containing all
the categories of the blog.
'''

import lpbm.datas.configmodel as cm_module
import lpbm.tools

class Category:
    '''
    Category's model in blog sources. Maps a section in an ini file containing
    all the categories of the blog. Basically, each category as a name and can
    have a parent category.
    '''
    name = cm_module.opt('name')
    parent = cm_module.opt_int('parent', default=None)

    def __init__(self, manager, id):
        self.manager, self.id, self.cm = manager, int(id), manager.cm
        self._full_name, self._level = None, None

    def __lt__(self, other):
        return (self.full_name() < other.full_name())

    def interactive(self):
        '''Interactively prompts the user for fields of the model.'''
        self.name = lpbm.tools.input_default('Name', self.name, required=True)
        self.manager.list_categories(short=True)
        known_categories = self.manager.categories.keys()
        def is_valid(value):
            '''This function validates the value entered for parent cat.'''
            try:
                ivalue = int(value)
            except ValueError:
                return False
            return (value is None or ivalue == -1 or ivalue in known_categories)
        self.parent = lpbm.tools.input_default('Parent', self.parent,
                                               is_valid=is_valid)
        if self.parent == -1:
            self.parent = None

    def full_name(self):
        '''This represent the path to the category, including parent's names.'''
        if self._full_name is not None:
            return self._full_name
        parent_fn = ''
        if self.parent is not None:
            parent_fn = self.manager.categories[self.parent].full_name() + ' > '
        return '{parent_fn}{name}'.format(
            parent_fn = parent_fn, name = self.name,
        )

    def level(self):
        '''The level of the category (number of its parents).'''
        if self._level is not None:
            return self._level
        if self.parent is None:
            self._level = 0
        else:
            self._level = 1 + self.manager.categories[self.parent].level()
        return self._level

    @property
    def section(self):
        '''Here for config manager.'''
        return str(self.id)
