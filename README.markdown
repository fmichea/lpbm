Lightweight Personal Blog Maker
===============================

This project aims to provide an easy way to generate static blog and personal
website using python scripts. Every page of the site is written using markdown,
to help formatting easily text.

This project is still under heavy development, and a lot of things aren't
fixed yet (meaning configuration file can change rapidly and often, for
example). Don't use it right now if you are not willing to spend some time fix
things between big updates.

This file only contains the minimum you need to know to install LPBM. A more
detailed documentation is provided in `doc/` directory, as a sphinx
documentation.

Features
--------

* LPBM is split in several sub-modules. Including configuration management,
  articles management, authors management and blog generation.
* You only need to know markdown to write articles. Every meta-data is stored
  in ini files, meaning you can manage them with any CVS.
* You can have any number of authors on articles, and any number of categories.
* Simple code embedding into articles. (using pygments).

Installation
------------

LPBM will soon be packaged with setup.py and PKGBUILD, and I will put it in AUR
too, when it will be ready for a Release Candidate.

### Install LPBM as a script.

For know, you can just clone this repository and link `~/.local/bin/lpbm` to
the lpbm.py file. Then you add `$HOME/.local/bin/` to your `PATH` environment
variable and you can execute LPBM everywhere.

### Install dependencies

You also must install `python` version 3, `pip` for python version 3 and all
the python library dependencies. To do this, you just have to execute `pip
install -r requirements.txt` and you'll have everything you need.

Usage
-----

There will be a detailed description of all the features and the usage of all
commands in the sphinx documentation in `doc/` directory.

Other information
-----------------

### Authors (v2)

* [Franck Michea](http://blog.kushou.eu/)

### Authors (v1)

* [Franck Michea](http://blog.kushou.eu/)
* [Pierre Bourdon](http://blog.delroth.net/)

### LPBM generates this blog:

* [LSE Blog](http://blog.lse.epita.fr/)

### Useful Links

* [Markdown Syntax](http://daringfireball.net/projects/markdown/syntax)
* [Code Embedding](http://packages.python.org/Markdown/extensions/code_hilite.html)
