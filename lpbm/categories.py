# categories.py - Category and category manager.

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

class CategoryManager(Category):
    def parse_category(self, cat):
        self.add_subcategory(cat.split('|'))
