Lightweight Personal Blog Maker
===============================

This project aims to provide an easy way to generate static blog and personnal
website using python scripts. Every page of the site is written using markdown,
to help formatting easily text.

In this READ, you will see SOURCES several times. By default it is in sources/
from the root of your clone, but you can change it in lpbm/constansts. Actually
you can change a lot of paths in this file.

By the way, this project is still under heavy developpement, and a lot of
things aren't fixed yet (meaning config file can change rapidly and often, for
example). Don't use it right now if you are not willing to spend some time fix
things between updates.

Features
--------

### Available

* Articles created with a unique *.markdown* file.
    * Unlimited authors and categories.
    * A permalink is based on article id (fixed if not changed).
* RSS Feed generated at /rssfeed.xml
* Author management based on logins.
    * Biographical pages availble.
* Simple code embedding (using pygments).
* Simple menu management.
    * Menu is generated using informations available in articles.

### Expected (TODO)

* Archives.
* Internationalization.
* Simple category management.
* User contributed pages, to build a simple website with the blog.

Usage
-----

### Configuration

Configuration can be set in the files SOURCES/config. It can contain blog
title, subtitle and footer (in this order). Syntax is s follow:

    [title: My blog title]
    [subtitle: My blog subtitle]
    [footer: My blog footer]
    [url: http://blog.example.com/]
    [disqus_id: id]

Keep line empty if you don't want to set a variable.

### Articles

Articles are represented by *.markdown* files. The header of the file can
contain informations such as id, authors and categories. Syntax is as follow:

    id: 1337
    author: login1
    [author: login2] ...
    category: Master1|Sub Category1
    [category: Master2|Sub Category2] ...
    title: Article Title
    [slug: slug]

    Article content...

*id* has a special meaning. When it is absent, article will be ignored, else it
will be used in permalink and for ordering articles (from highest to lower).
Each author and category must be on their own lines, authors first. No new line
between authors and categories.

*slug* is there if you want to change the title of your article without
breaking permalinks.

### Authors

You can set some variables to authors, like his name, email or bio. A file to
describe an author should be placed in SOURCES/authors/*login*.markdown with
*login* replaced correctly. Syntax is as follow:

    name: Your Name Here
    email: your.email@example.com

    [bio (markdown)]

Other information
-----------------

### Authors

* [Pierre Bourdon](http://blog.delroth.net/)
* [Franck Michea](http://blog.kushou.eu/)

### Useful Links

* [Markdown Syntax](http://daringfireball.net/projects/markdown/syntax)
* [Code Embedding](http://packages.python.org/Markdown/extensions/code_hilite.html)

### Dependencies

Library used:

* **PyRSS2Gen**: RSS Generator. ([http://www.dalkescientific.com/Python/PyRSS2Gen.html](http://www.dalkescientific.com/Python/PyRSS2Gen.html))
* **Jinja2**: Template engine. ([http://jinja.pocoo.org/](http://jinja.pocoo.org/))

These programs are executed by the script.

* **sass**: SCSS to CSS Translator in ruby.
* **pygmentize**: Gets pygment's stylesheet.
