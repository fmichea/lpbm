# paginate.py - Paginate articles.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import math
import os

import lpbm.constants


class Paginate(object):
    def __init__(self, template, articles, tpl_name, output_dir,
                 title_prefix=None):
        self.template = template
        self.tpl_name = tpl_name
        self.output_dir = output_dir
        self.title_prefix = title_prefix

        # Compute pages.
        self.articles = articles
        self.pages = int(math.ceil(
            len(self.articles) / float(lpbm.constants.ART_BY_PAGE)
        ))

    def left_stone(self, nb):
        nb -= 1
        return max(
            max(0, nb - lpbm.constants.WIDTH_PAGINATE / 2),
            self.pages - lpbm.constants.WIDTH_PAGINATE
        )

    def right_stone(self, nb):
        nb -= 1
        return min(
            min(self.pages, nb + lpbm.constants.WIDTH_PAGINATE / 2),
            lpbm.constants.WIDTH_PAGINATE - 1
        )

    def render(self):
        pages = range(1, self.pages + 1)

        self.template.init_template(self.tpl_name)
        for page in pages:
            if self.title_prefix is not None:
                title = self.title_prefix + ' - '
            else:
                title = ''
            title += 'Index' if page == 1 else 'Page %d' % page
            self.template.render('%s/%d.html' % (self.output_dir, page), {
                'page_title': title,
                'articles': self.articles[
                    (page - 1) * lpbm.constants.ART_BY_PAGE:
                    page * lpbm.constants.ART_BY_PAGE
                ],
                'paginate': True,
                'directory': self.output_dir,
                'pages': pages[self.left_stone(page):self.right_stone(page) + 1],
                'cur_page': page,
                'first_page': 1,
                'last_page': self.pages,
            })

        try:
            os.symlink('1.html', os.path.join(
                lpbm.constants.ROOT_OUTPUT, self.output_dir, 'index.html'
            ))
        except OSError:
            pass
