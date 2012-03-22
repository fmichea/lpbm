# author.py - Author model and manager.

import os
import re
import markdown
import codecs

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

        author_file = os.path.join(lpbm.constants.ROOT_SRC_AUTHORS,
                                   '%s.markdown' % login)
        try:
            f = codecs.open(author_file, 'r', 'utf-8')
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

    def get_description(self):
        if self.bio == '':
            self.bio = 'No Description Available\n=======\nWe are sorry, but no description'
            self.bio += ' is available for this author.'
        return markdown.markdown(self.bio)

class AuthorsManager(object):
    def __init__(self):
        self.authors = dict()

    def add_author(self, login):
        if login not in self.authors:
            self.authors[login] = Author(login)

    def get_authors(self):
        return self.authors.values()
