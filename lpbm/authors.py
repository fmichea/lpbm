# author.py - Author model and manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

# FIXME: Clean me!
#import os
#import re
#import markdown
#import codecs
#
#import lpbm.constants
#
## Exceptions
#class AuthorError(Exception):
#    def __init__(self, login):
#        self.login = login
#
#    def __str__(self):
#        return  self.message.format(login = self.login)
#
#class AuthorUndefinedError(AuthorError):
#    message = 'Author `{login}\' is not defined.'
#
#class AuthorUndefinedNameError(AuthorError):
#    message = 'Author `{login}\' has no name defined.'
#
#class AuthorUndefinedMailError(AuthorError):
#    message = 'Author `{login}\' has no mail defined.'

import functools

def _input_default(prompt, default):
    tmp = input('{prompt} [{default}]: '.format(
        prompt = prompt, default = default,
    ))
    if not tmp:
        tmp = default
    return tmp

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

    # FIXME: Remove me.
#    def ex__init__(self, login):
#        self.login = login
#
#        author_file = os.path.join(lpbm.constants.ROOT_SRC_AUTHORS,
#                                   '%s.markdown' % login)
#        try:
#            f = codecs.open(author_file, 'r', 'utf-8')
#            lines = f.readlines()
#        except IOError:
#            raise AuthorUndefinedError(login)
#
#        frmt = re.compile('^name: (%s)$' % lpbm.constants.FRMT_NAME)
#        try: match = frmt.match(lines[0])
#        except IndexError: raise AuthorUndefinedNameError(login)
#        if match is not None: self.name = match.group(1)
#        else: raise AuthorUndefinedNameError(login)
#
#        frmt = re.compile('^email: (%s)$' % lpbm.constants.FRMT_EMAIL)
#        try:
#            match = frmt.match(lines[1])
#            if match is not None:
#                self.email = match.group(1)
#            else:
#                self.email = None
#        except IndexError: pass


# FIXME: Remove me....
#class AuthorsManager(object):
#    def __init__(self):
#        self.authors = dict()
#
#    def add_author(self, login):
#        if login not in self.authors:
#            self.authors[login] = Author(login)
#
#    def __iter__(self):
#        return iter(self.authors.values())
