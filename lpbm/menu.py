# menu.py - Generates a simple menu with categories, authors and archives.
# Author: Franck Michea < franck.michea@gmail.com >

import lpbm.constants

class Menu(object):
    def __init__(self, cat_mgr, aut_mgr):
        self.cat_mgr = cat_mgr
        self.aut_mgr = aut_mgr

    def get_categories(self):
        def browse_categories(cat, indent=0):
            tmp = ''
            for _, sub in cat.sub.items():
                tmp += browse_categories(sub, indent + 1)
            if tmp != '':
                tmp = '<ul>\n%s\n</ul>' % tmp
            return '{i}<li><a href="#">{title}</a>\n{sub}\n{i}</li>'.format(
                i = '\t' * indent, title = cat.name,
                sub = '\n'.join(map(
                    lambda a: '%s%s' % ((indent + 1) * '\t', a),
                    tmp.splitlines()
                ))
            )

        # Categories.
        res = browse_categories(self.cat_mgr)
        tmp = res.splitlines()
        tmp[0] = '<div id="categories"><strong>{}</strong>\n<ul>'.format(
            self.cat_mgr.name
        )
        tmp[-1] = '</ul>\n</div>'
        return ('\n'.join(tmp))
