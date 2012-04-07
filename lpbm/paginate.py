# paginate.py - Paginate articles.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import math

import lpbm.constants


class Paginate(object):
    def __init__(self, template, article_mgr):
        self.template = template
        self.article_mgr = article_mgr

        # Compute pages.
        self.articles = self.article_mgr.get_articles()
        self.pages = int(math.ceil(
            len(self.articles) / float(lpbm.constants.ART_BY_PAGE)
        ))

    def left_stone(self, nb):
        nb -= 1
        return min(
            max(0, nb - lpbm.constants.WIDTH_PAGINATE / 2),
            self.pages - lpbm.constants.WIDTH_PAGINATE
        )

    def right_stone(self, nb):
        nb -= 1
        return max(
            min(self.pages, nb + lpbm.constants.WIDTH_PAGINATE / 2),
            lpbm.constants.WIDTH_PAGINATE - 1
        )

    def render(self):
        pages = range(1, self.pages + 1)

        self.template.init_template('articles', 'base.html')
        for page in pages:
            self.template.render('pages/%d.html' % page, {
                'page_title': 'Index' if page == 1 else 'Page %d' % page,
                'articles': self.articles[
                    (page - 1) * lpbm.constants.ART_BY_PAGE:
                    page * lpbm.constants.ART_BY_PAGE
                ],
                'paginate': True,
                'pages': pages[self.left_stone(page):self.right_stone(page) + 1],
                'cur_page': page,
                'first_page': 1,
                'last_page': self.pages,
            })
