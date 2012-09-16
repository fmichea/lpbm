# author.py - Author model and manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import lpbm.datas.configmodel as cm_module
import lpbm.tools

class Author:
    id = cm_module.opt_int('id')
    last_name = cm_module.opt('last_name', default='')
    first_name = cm_module.opt('first_name', default='')
    email = cm_module.opt('email')

    def __init__(self, nickname, config):
        self.nickname, self.cm = nickname, config

    def __lt__(self, other):
        return (self.last_name < other.last_name or
                self.first_name < other.first_name)

    def interactive(self):
        self.first_name = lpbm.tools.input_default('First name', self.first_name)
        self.last_name = lpbm.tools.input_default('Last name', self.last_name)
        self.email = lpbm.tools.input_default('Email', self.email)

    @property
    def section(self):
        return self.nickname
