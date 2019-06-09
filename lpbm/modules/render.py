# lpbm/modules/articles.py - Loads articles and treats them.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import os

import lpbm.module_loader
import lpbm.tools as ltools

from lpbm.lib.deprecated_command import deprecated_command


class Render(lpbm.module_loader.Module):
    def name(self): return 'render'

    def abstract(self): return 'Blog generation module.'

    def init(self):
        self.needed_modules = ['authors', 'articles', 'categories']

        self.parser.add_argument('-d', '--drafts', action='store_true',
                                 default=False, help='also render drafts.')
        self.parser.add_argument('-t', '--theme', action='store',
                                 help='Try a theme to generate the blog.')
        output_help = 'change default output directory (absolute from $PWD).'
        self.parser.add_argument('-o', '--output', action='store',
                                 metavar='directory', help=output_help)
        self.parser.add_argument('-i', '--id', action='store',
                                 help='render a specific article.')
        noconfirm_help = 'do not confirm to empty output directory.'
        self.parser.add_argument('-N', '--noconfirm', action='store_true',
                                 default=False, help=noconfirm_help)

    def load(self, modules, args):
        pass

    def process(self, modules, args):
        deprecated_command()
