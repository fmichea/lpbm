# author.py - Author model and manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import functools

p = functools.partial

class Author(object):
    def __init__(self, nickname, config):
        self.nickname = nickname
        self.config = config
        if not self.config.has_section(nickname):
            self.config.add_section(nickname)

    def interactive(self):
        self.first_name = _input_default('First name', self.first_name)
        self.last_name = _input_default('Last name', self.last_name)
        self.email = _input_default('Email', self.email)

    def __lt__(self, other):
        return (author.last_name < other.last_name or
                author.first_name < other.first_name)

    def set_opt(self, value, opt):
        self.config.set(self.nickname, opt, value)

    def get_opt(self, opt, fb=''):
        return self.config.get(self.nickname, opt, fallback=fb)

    last_name = property(p(get_opt, opt='last_name'), p(set_opt, opt='last_name'))
    first_name = property(p(get_opt, opt='first_name'), p(set_opt, opt='first_name'))
    email = property(p(get_opt, opt='email'), p(set_opt, opt='email'))
