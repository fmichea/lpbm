# author.py - Author model and manager.

import os
import re

import lpbm.constants

# Exceptions
class AuthorError(Exception):
    def __init__(self, login):
        self.login = login

    def __str__(self):
        return  self.message.format(login = self.login)

class AuthorUndefinedError(AuthorError):
    message = 'Author `{login}\' is not defined.'

class AuthorUndefinedNameError(AuthorError):
    message = 'Author `{login}\' has no name defined.'

class AuthorUndefinedMailError(AuthorError):
    message = 'Author `{login}\' has no mail defined.'


class Author(object):
    def __init__(self, login):
        self.login = login

        author_file = os.path.join(lpbm.constants.ROOT_AUTHORS,
                                   '%s.markdown' % login)
        try:
            with open(author_file) as f:
                lines = f.readlines()
        except IOError:
            raise AuthorUndefinedError(login)

        frmt = re.compile('^name: (%s)$' % lpbm.constants.FRMT_NAME)
        try: match = frmt.match(lines[0])
        except IndexError: raise AuthorUndefinedNameError(login)
        if match is not None: self.name = match.group(1)
        else: raise AuthorUndefinedNameError(login)

        frmt = re.compile('^email: (%s)$' % lpbm.constants.FRMT_EMAIL)
        try:
            match = frmt.match(lines[1])
            if match is not None:
                self.email = match.group(1)
            else:
                self.email = None
        except IndexError: pass

        self.bio = ''.join(lines[2:])


class AuthorsManager(object):
    def __init__(self):
        self.authors = dict()

    def add_author(self, login):
        if login not in self.authors:
            self.authors[login] = Author(login)
