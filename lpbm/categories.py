# categories.py - Category and category manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import lpbm.constants
import lpbm.paginate

class Category(object):
    def __init__(self, name, parent=None):
        self.name = name
        self.articles = []
        self.sub = dict()
        self.parent = parent

    @property
    def slug(self):
        slug = self.name.lower().replace(' ', '-')
        slug = ''.join(c for c in slug if c in lpbm.constants.SLUG_CHARS)
        slug = slug[:lpbm.constants.SLUG_SIZE]
        if self.parent is not None and self.parent.parent is not None:
            slug = self.parent.slug + '-' + slug
        return slug

    @property
    def url(self):
        return "/cat/%s/" % self.slug

    @property
    def accumulated_articles(self):
        articles = self.articles[:]
        for sub in self.sub.itervalues():
            articles.extend(sub.accumulated_articles)
        return sorted(articles)

    def add_subcategory(self, cat):
        if cat == []:
            return self
        if cat[0] not in self.sub:
            self.sub[cat[0]] = Category(cat[0], self)
            return self.sub[cat[0]]
        return self.sub[cat[0]].add_subcategory(cat[1:])

    def __iter__(self):
        return iter(sorted(self.sub.values(),
                           cmp=lambda a, b: cmp(a.name, b.name)))


    def render(self, template):
        self.render_children(template)
        p = lpbm.paginate.Paginate(template, self.accumulated_articles,
                                   'articles/base.html',
                                   'cat/%s' % self.slug,
                                   title_prefix=self.name)
        p.render()

    def render_children(self, template):
        for cat in self.sub.itervalues():
            cat.render(template)

class CategoryManager(Category):
    def parse_category(self, cat):
        return self.add_subcategory(cat.split('|'))

    def render(self, template):
        return self.render_children(template)
