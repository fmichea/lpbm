# lpbm/datas/categories.py - Category model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import lpbm.datas.configmodel as cm_module
import lpbm.tools

class Category:
    name = cm_module.opt('name')
    parent = cm_module.opt_int('parent', default=None)

    def __init__(self, manager, id):
        self.manager, self.id, self.cm = manager, int(id), manager.cm
        self._full_name, self._level = None, None

    def __lt__(self, other):
        return (self.full_name() < other.full_name())

    def interactive(self):
        self.name = lpbm.tools.input_default('Name', self.name, required=True)
        self.manager.list_categories(short=True)
        known_categories = self.manager.categories.keys()
        def is_valid(value):
            return (value is None or int(value) in known_categories)
        self.parent = lpbm.tools.input_default('Parent', self.parent,
                                               is_valid=is_valid)

    def full_name(self):
        if self._full_name is not None:
            return self._full_name
        parent_fn = ''
        if self.parent is not None:
            parent_fn = self.manager.categories[self.parent].full_name() + ' > '
        return '{parent_fn}{name}'.format(
            parent_fn = parent_fn, name = self.name,
        )

    def level(self):
        if self._level is not None:
            return self._level
        if self.parent is None:
            self._level = 0
        else:
            self._level = 1 + self.manager.categories[self.parent].level()
        return self._level

    @property
    def section(self):
        return str(self.id)
