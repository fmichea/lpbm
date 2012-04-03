# categories.py - Category and category manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

class Category(object):
    def __init__(self, name):
        self.name = name
        self.articles = []
        self.sub = dict()

    def add_subcategory(self, cat):
        if cat == []:
            return
        if cat[0] not in self.sub:
            self.sub[cat[0]] = Category(cat[0])
        self.sub[cat[0]].add_subcategory(cat[1:])

    def __iter__(self):
        return iter(self.sub.values())


class CategoryManager(Category):
    def parse_category(self, cat):
        self.add_subcategory(cat.split('|'))
