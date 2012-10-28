# lpbm/exceptions.py - All the errors that can be raised in the program.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)


class NoSuchAuthorError(Exception):
    def __init__(self, idx):
        self.idx = idx

    def __str__(self):
        return 'This author doesn\'t exist. (id = {})'.format(self.idx)
