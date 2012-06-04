# rss.py - RSS generator.
# Author: Franck Michea < franck.michea@gmail.com >
# License: New BSD License (See LICENSE)

import datetime
import os
import PyRSS2Gen

import lpbm.config
import lpbm.constants

CONFIG = lpbm.config.Config()
AUTHOR_MGR = None

def rss_item(article):
    # Generating author list.
    tmp = []
    for author_login in article.authors:
        author = AUTHOR_MGR.authors[author_login]
        tmp.append('%s (%s)' % (author.email, author.name))
    authors = ', '.join(tmp)

    # The article.
    return PyRSS2Gen.RSSItem(
        title = article.title,
        link = '%s%s' % (CONFIG.url, article.get_filename()),
        author = authors,
        guid = str(article.pk),
        description = article.get_content(),
        pubDate = article.crt_date,
    )

def render(art_mgr, aut_mgr, cat_mgr):
    global AUTHOR_MGR
    AUTHOR_MGR = aut_mgr

    rss = PyRSS2Gen.RSS2(
        title = CONFIG.title,
        link = CONFIG.url,
        description = CONFIG.subtitle,
        lastBuildDate = datetime.datetime.now(),
        items = map(rss_item, art_mgr.get_articles()[:CONFIG.rss_articles])
    )
    f = open(os.path.join(lpbm.constants.ROOT_OUTPUT, 'rssfeed.xml'), 'w')
    rss.write_xml(f)
    f.close()
