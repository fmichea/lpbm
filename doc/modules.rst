=========================================
Modules: all you need to know to use lpbm
=========================================

You finally installed lpbm and you want to write your first blog post? You are
in the right place. In this documentation I will explain you in great details
how lpbm works and how you should use it, end-user wise.

Introduction
------------

General options
^^^^^^^^^^^^^^^

There are very few generic options applied directly to lpbm. Actually they are
mostly there for debugging purpose:

.. code-block:: console

    $ lpbm --help
    usage: lpbm [-h] [-b] [-d] [-p EXEC_PATH] [-P]
            {articles,authors,categories,config,render} ...

    Lightweight Personal Blog Maker

    positional arguments:
      {articles,authors,categories,config,render}
        articles            Loads and manipulates articles.
        authors             Loads, manipulates and renders authors.
        categories          Loads and manipulates categories.
        config              Manipulates blog configuration.
        render              Blog generation module.

    optional arguments:
      -h, --help            show this help message and exit
      -b, --backtrace       print backtrace on error (default with pdb).
      -d, --debug           print debug information.
      -p EXEC_PATH, --exec-path EXEC_PATH
                            path where lpbm will search the blog. (default: .)
      -P, --pdb             start pdb debugger on exception.

With options ``--backtrace`` and ``--pdb``, you can debug easily lpbm when it
raises exceptions. If you consider reporting a bug, giving the output of lpbm
with ``--backtrace`` would help me debug a lot.

The option ``--debug`` is there for logging purposes, but currently only module
loading is logged correctly. This will be fixed in the future.

Finally you can use ``--exec-path`` to reference your blog path directly on
command line without having to change directory (to manipulate your blog from
another directory).

Modules
--------

Model/Object Manager Modules
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

This special type of module has only one purpose: interact with the user to
create, modify and delete objects. An object is an author, or an article, or a
category. They all have 6 common arguments, which are ``--list``, ``--new``,
``--id id``, ``--edit``, ``--delete`` and ``--with-deleted``.

They can be separated in three groups: stand-alone options, flags and specific
options applied on an object.

- ``--list`` will list all the known objects.
- ``--new`` will interactively prompt you for information about the attributes
  of the object you are creating.

- ``--edit`` will help you edit meta-data of a certain object. You must precise
  ``--id id`` to select the object. You can fetch the id of an object with list.
- ``--delete`` will delete the object from following listing. Object will always
  stay in files, to avoid id collision and the like. If you really want to
  remove something, remove the files and references in configurations. Like
  ``--edit``, it needs ``--id`` option.

- ``--with-deleted`` is just a flag, saying true or false. It modifies the
  behavior of listings to include deleted objects again in them.

Finally, ``articles`` module as several more options, like something to edit the
article (markdown) or something to publish an article. You can check its help.

Other modules
^^^^^^^^^^^^^

There are two other modules that are ``config`` module and ``render`` module.
The first one helps you manage and check the configuration of you blog. The
second one is to render the blog.

Interactive mode
----------------

Since the only way you can interact with lpbm (without modifying configuration
files) with with its built-in prompt, it has several behaviors you need to know.

First, you have several information in the prompt::

    Prompt 1 (required) [default value]:
    Prompt 2 []:
    Prompt 3 (required) []:

In this example, we can see that first field we fill is required. It also
already has a default value that is write between ``[]`` brackets. Simply
entering without filling Prompt 1 will choose default value. You should'nt
be able to validate an empty value for Prompt 3 (if you can, fill a bug :P).

There are also validators that will check that the values you enter are valid.
If some prompt appears twice, the value was not valid. There should be a error
message explaining what went wrong. If it is not the case, please fill a bug.

Finally if your value is not required and you want to delete the content (avoid
selectionning default value), type Ctrl-D and answer yes to the question asking
you if you want to empty the value.

Any keyboard interruption should quit the interctive mode without saving
anything.
