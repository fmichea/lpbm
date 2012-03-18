Lightweight Personal Blog Maker
===============================

This project aims to provide an easy way to generate static blog and personnal
website using python scripts. Every page of the site is written using markdown,
to help formatting easily text.

Features (expected)
-------------------

* Archives.
* Articles created with a unique *.markdown* file.
* Author management based on logins.
* Internationalization.
* Simple category management.
* Simple code embedding (using pygments).
* Simple menu management.
* User contributed pages, to build a simple website with the blog.

Usage
-----

### Articles

Articles are represented by *.markdown* files. The header of the file can
contain informations such as authors and categories. Syntax is as follow:

    author: login1
    [author: login2] ...
    category: Master1|Sub Category1
    [category: Master2|Sub Category2] ...

    Article Title
    =============

    Article content...

Each author and category must be on their own lines, authors first. Ne new line
between authors and categories.

Authors
-------

* [Franck Michea](http://blog.kushou.eu)

Useful Links
------------

* [Markdown Syntax](http://daringfireball.net/projects/markdown/syntax)
