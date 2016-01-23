# lpbm/datas/categories.py - Category model.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Category's model in blog sources. Maps a section in an ini file containing all
the categories of the blog.
'''

import os

import lpbm.models.configmodel as cm_module
import lpbm.tools as ltools


class Category(cm_module.Model):
    '''
    Category's model in blog sources. Maps a section in an ini file containing
    all the categories of the blog. Basically, each category as a name and can
    have a parent category.
    '''

    parent = cm_module.opt_int('parent', default=None)
    slug = cm_module.opt('slug', required=True)

    def __init__(self, mod, mods, name):
        super().__init__(mod, mods)
        self.cm, self.name = mod.cm, name
        self._full_path, self._level = None, None
        self._interactive_fields = ['section', 'slug', 'parent']

    def __lt__(self, other):
        return (self.full_name() < other.full_name())

    def __str__(self):
        return self.name

    def full_path(self):
        if self._full_path is None:
            self._full_path = []
            if self.parent is not None:
                self._full_path.extend(self.mod[self.parent].full_path())
            self._full_path.append(self)
        return self._full_path

    def full_name(self):
        '''This represent the path to the category, including parent's names.'''
        return ' > '.join(it.name for it in self.full_path())

    def level(self):
        '''The level of the category (number of its parents).'''
        if self._level is None:
            if self.parent is None:
                self._level = 0
            else:
                self._level = 1 + self.mod[self.parent].level()
        return self._level

    def list_verbose(self):
        return '\r{indent}{id:2d} - {cat}'.format(
            cat=str(self),
            id=self.id,
            indent='  ' * self.level(),
        )

    def interactive_section(self):
        def is_valid(value):
            f = self.mod.cm.config.has_section
            return value == self.name or not f(value)
        old_name = self.name
        self.name = ltools.input_default('Name', self.name, required=True,
                                         is_valid=is_valid)
        if self.name != old_name:
            self.mod.cm.config.remove_section(old_name)

    def interactive_parent(self):
        self.mod.opt_list(short=True)
        super()._interactive_field('parent')

    def interactive_parent_is_valid(self, value):
        ids = [obj.id for obj in self.mod.objects]
        try:
            return value is None or int(value) in ids
        except ValueError:
            return False

    def interactive_slug(self):
        def is_valid(value):
            if value != ltools.slugify(value):
                print('This is not a valid slug.')
                return False
            return True
        default = self.slug or ltools.slugify(self.name)
        self.slug = ltools.input_default('Slug', default, required=True,
                                         is_valid=is_valid)

    def html_filename(self):
        slugs = [cat.slug for cat in self.full_path()]
        return 'cat/{}/index.html'.format(os.path.join(*slugs))

    def url(self):
        return '/{}'.format(self.html_filename())

    @property
    def section(self):
        '''Here for config manager.'''
        return self.name
