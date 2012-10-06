# author.py - Author model and manager.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

'''
Author's model in blog sources. Maps a section in an ini file containing all
authors of the blog.
'''

import lpbm.datas.configmodel as cm_module
import lpbm.tools as ltools

class Author:
    '''
    Author's model in blog sources. Maps a section in an ini file containing
    all authors of the blog.
    '''

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
        '''Interactively prompts the user for fields of the model.'''
        self.first_name = ltools.input_default('First name', self.first_name)
        self.last_name = ltools.input_default('Last name', self.last_name)
        self.email = ltools.input_default('Email', self.email)

    @property
    def section(self):
        '''Here for config manager.'''
        return self.nickname
