# author.py - Author model and manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Author's model in blog sources. Maps a section in an ini file containing all
authors of the blog.
'''

import lpbm.models.configmodel as cm_module
import lpbm.tools as ltools

class Author(cm_module.Model):
    '''
    Author's model in blog sources. Maps a section in an ini file containing
    all authors of the blog.
    '''

    last_name = cm_module.opt('last_name', default='')
    first_name = cm_module.opt('first_name', default='')
    email = cm_module.opt('email')

    def __init__(self, mod, mods, nickname):
        super().__init__(mod, mods)
        self.nickname, self.cm = nickname, mod.cm

        # Model interactive fields.
        self._interactive_fields += ['section', 'first_name', 'last_name', 'email']

    def __lt__(self, other):
        return (self.last_name < other.last_name or
                self.first_name < other.first_name)

    def __str__(self):
        res = self.full_name()
        if res != self.nickname:
            res += ' a.k.a. {nickname}'.format(nickname = self.nickname)
        if self.email is not None:
            res += ' [{email}]'.format(email = self.email)
        return res

    def full_name(self):
        if self.first_name and self.last_name:
            return '{} {}'.format(self.first_name, self.last_name)
        elif self.first_name:
            return self.first_name
        else:
            return self.nickname

    def interactive_section(self):
        def is_valid(value):
            f = self.mod.cm.config.has_section
            return value == self.nickname or not f(value)
        old_nick = self.nickname
        self.nickname = ltools.input_default('Nickname', self.nickname,
                                             required=True, is_valid=is_valid)
        if self.nickname != old_nick:
            self.mod.cm.config.remove_section(old_nick)

    @property
    def section(self):
        '''Here for config manager.'''
        return self.nickname
