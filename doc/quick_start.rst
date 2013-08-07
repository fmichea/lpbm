=====================================
Quick Start: Step-by-step quick start
=====================================

Start configuration
-------------------

First go into a folder wherever you want. I personally named it
``/tmp/my_first_blog`` (if this path is somewhere below, you will know that this
is the root of my blog). The directory is empty.

We will first need to fill few variables in the configuration. You can always
check your configuration using ``lpbm config -k``. This is what I did:

.. code-block:: console

    $ touch lpbm.cfg
    $ lpbm config --set general.title="kushou's blog"
    $ lpbm config --set general.url="http://localhost:8081/"

You now have the minimum required configuration. You can also check what other
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
``lpbm articles --id 0 --publish``.

Render your new blog!
---------------------

Now you have your blog ready for rendering! You now have multiple choices to do
so.

#. Create a directory/symbolic link named ``result`` in your blog sources. This
   directory will be used as the output for the *render* command.
#. Precise the output directory easily.

.. warning:: Be careful! LPBM will delete **everything** in the output
             directory. Create it only for the blog, and avoid modifying it
             directly. You've been warned.

Testing setup
^^^^^^^^^^^^^

When we are writing our article, the simplest setup is probably to create a
output directory, ``result``, and launch the simple HTTP server shipped with
python in it. Example, in another shell:

.. code-block:: console

    $ mkdir result; cd result
    $ python -m http.server
    Serving HTTP on 0.0.0.0 port 8000 ...

You can get back to your blog and render it with ``lpbm render`` command. It
will warn you again that it will remove the contents of the directory. Say yes
if you are sure, alternatively you can precise ``-N`` to never be asked this
again. You know what you're doing from now on.

You'll notice that the rending can take some time if you have a lot of articles,
and if they are quite big, so you also can choose one articles to render. This
can be done with the ``-i`` switch that takes an id as a parameter.

If you want to render the whole blog, including drafts, you can finally include
the ``--draft`` switch to do so.

Production
^^^^^^^^^^

For your production setup, you won't need any fancy web server or anything. You
will just need something that is able to serve static HTML pages. Here is an
example configuration to serve it with ``nginx``:

.. code-block:: nginx

    server {
        listen 80;
        listen [::]:80; # If your nginx is old, you only need the IPv6 one (that
                        # does both)
        server_name blog.example.com;

        access_log /var/log/nginx/blog.example.com.access.log;
        error_log /var/log/nginx/blog.example.com.error.log;

        location / {
            root /srv/http/blog.example.com;
            index index.html index.htm;
        }
    }

Then you just need to have your blog somewhere, say ``~/blog-articles`` and do
``lpbm -p ~/blog-articles render -N -o /srv/http/blog.example.com`` when you
published a new article. This process can be automated if you have your blog
articles in a *git*, etc.

Random end notes
----------------

If you find any bug again don't hesitate to get back to me, you have my mail ;).
The ``touch`` and ``mkdir`` should be removed soon, and done directly by lpbm.
Have fun!
