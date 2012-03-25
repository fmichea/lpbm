# config.py - Loads configuration.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import re
import os

import lpbm.constants

class Config(object):
    def __init__(self):
        try:
            with open(os.path.join(lpbm.constants.ROOT_SOURCES, 'config')) as f:
                lines = f.readlines()
        except IOError: lines = []

        # Get title of the blog.
        try: self.title = re.match('^title: (.+)$', lines[0]).group(1)
        except (IndexError, AttributeError): self.title = 'No Title Defined'

        try: self.subtitle = re.match('^subtitle: (.+)$', lines[1]).group(1)
        except (IndexError, AttributeError): self.subtitle = 'Subtitle'

        try: self.footer = re.match('^footer: (.+)$', lines[2]).group(1)
        except (IndexError, AttributeError): self.footer = 'Footer'

        try: self.disqus_id = re.match('^disqus_id: (.+)$', lines[3]).group(1)
        except (IndexError, AttributeError): self.disqus_id = None
