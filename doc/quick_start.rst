=====================================
Quick Start: Step-by-step quick start
=====================================

Start configuration
-------------------

First go into a folder wherever you want. I personally named it
``/tmp/my_first_blog`` (if this path is somewhere below, you will know that this
is the root of my blog). The directory is empty.

We will first need to fill few variables in the configuration. You can always
check your configuration using ``lpbm config -k``. This is what I did::

    $ touch lpbm.cfg
    $ lpbm config --set general.title="kushou's blog"
    $ lpbm config --set general.url="http://localhost:8081/"

You know have the minimum configuration necessary. You can also check what other
option is available. You can for example add a twitter account or disqus account
for tweet button and comments.

Create your first author
------------------------

We will now add our first author, our account. There is nothing more simple: you
just have to type ``lpbm authors --new`` and it will prompt you with several
questions. Here is a concrete example:

.. code-block:: console

    $ lpbm authors --new
    Id (required) [0]: 
    Nickname (required) []: kushou
    First Name []: Franck
    Last Name []: Michea
    Email []: franck.michea@gmail.com

And now we can check that we are correctly created by listing authors with
``lpbm authors --list`` command.

.. code-block:: console

    $ lpbm authors -l
    All authors:
      0 - Franck Michea a.k.a. kushou [franck.michea@gmail.com]

Works!

Create your first categories
----------------------------

Now it will begin to be hard. You will have to decide a first subject that will
become category on your blog. Lets say Music, with two sub-categories, how about
some Metal and some Progressive Trance articles? Here you go:

.. code-block:: console

    $ lpbm categories -n
    Id (required) [0]: 
    Name (required) []: Music
    Slug (required) [music]: 
     + There is no category.
    Parent []: 
    $ lpbm categories -n
    Id (required) [1]: 
    Name (required) []: Metal
    Slug (required) [metal]: 
     0 - Music
    Parent []: 0
    $ lpbm categories -n
    Id (required) [2]: 
    Name (required) []: Progressive Trance
    Slug (required) [progressive-trance]: 
     0 - Music
       1 - Metal
    Parent []: 0
    $ lpbm categories -l
    All categories:
     0 - Music
       1 - Metal
       2 - Progressive Trance

As you can see, categories were created pretty easily. We can now write our
first article!

Create your first article
-------------------------

If everything went OK until this step, this is nice! I now want to write some
article about Chris Adler, the drummer of the band Lamb of God. This article
will land in my Metal category. Lets see:

.. code-block:: console

    $ mkdir articles
    $ lpbm articles -n
    Id (required) [0]: 
    Title (required) []: Chris Adler: Lamb of God awesome drummer.
    Filename (required) [chris-adler-lamb-of-god-awesome-drummer]: 
      0 - Franck Michea a.k.a. kushou [franck.michea@gmail.com]
    Please list authors (comma separated) (required) []: 0
     0 - Music
       1 - Metal
       2 - Progressive Trance
    Please list categories (comma separated) (required) []: 1
    Article was successfully created!
    Do you want to edit it right now? [y/N] y

I said yes but you can obviously say no and edit it later. You can list all
articles with ``lpbm articles -l`` and also edit the markdown of our newly
created article using ``lpbm articles --id 0 -E``. You can also publish it with
``lpbm articles --publish``.

Render your new blog!
---------------------

Now you have your blog ready for rendering! Try it now: ``lpbm render``. This
will need a ``result`` directory or symlink to the place were you want your blog
to be generated. you can then open ``result/index.html`` in your browser.

I foster you to configure a simple HTTP server (no need of any dynamique
language, just static files serving is fine) to see CSS and the like correctly.

Random end notes
----------------

If you find any bug agin don't hesitate to get back to me, you have my mail ;).
The ``touch`` and ``mkdir`` should be removed soon, and done directly in lpbm.
Have fun!
