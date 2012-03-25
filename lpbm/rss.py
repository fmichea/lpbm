# rss.py - RSS generator.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import datetime
import os
import PyRSS2Gen

import lpbm.config
import lpbm.constants

CONFIG = lpbm.config.Config()

def rss_item(article):
    return PyRSS2Gen.RSSItem(
        title = article.title,
        link = '%s%s' % (CONFIG.url, article.get_url()),
        guid = '%s%s' % (CONFIG.url, article.get_url()),
        description = article.get_content(),
        pubDate = article.mod_date,
    )

def render(art_mgr, aut_mgr, cat_mgr):
    rss = PyRSS2Gen.RSS2(
        title = CONFIG.title,
        link = CONFIG.url,
        description = CONFIG.subtitle,
        lastBuildDate = datetime.datetime.now(),
        items = map(rss_item, art_mgr.get_articles())
    )
    f = open(os.path.join(lpbm.constants.ROOT_OUTPUT, 'rssfeed.xml'), 'w')
    rss.write_xml(f)
    f.close()
