# rss.py - RSS generator.
# Author: Franck Michea < franck.michea@gmail.com >

import datetime
import os
import PyRSS2Gen

import lpbm.constants

def rss_item(article):
    return PyRSS2Gen.RSSItem(
        title = article.title,
        link = ('/articles/%d.html' % article.pk),
        guid = ('/articles/%d.html' % article.pk),
        description = article.get_content(),
        pubDate = article.mod_date,
    )

def render(art_mgr, aut_mgr, cat_mgr):
    config = lpbm.config.Config()
    rss = PyRSS2Gen.RSS2(
        title = config.title,
        link = 'http://localhost/',
        description = config.subtitle,
        lastBuildDate = datetime.datetime.now(),
        items = map(rss_item, art_mgr.get_articles())
    )
    f = open(os.path.join(lpbm.constants.ROOT_OUTPUT, 'rssfeed.xml'), 'w')
    rss.write_xml(f)
    f.close()
