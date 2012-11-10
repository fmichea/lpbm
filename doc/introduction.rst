Introduction
============

lpbm - Lightweight Personal Blog Maker
--------------------------------------

Welcome to the documentation of lpbm. This project aims to provide a simple way
to generate a static blog based on markdown written articles.

The main idea of this is that you write your article in an enhanced version of
text files, and this project helps you manage them and generate a bunch of html
files that make a nice little blog.

This approach is interesting for few reasons:

 * First you don't need to use any program to write your articles. Indeed, your
   standard editor (the one in which you write text or code) will just do.
 * Since articles and lpbm files are basically text files, you can use whatever
   you want to sync them. Indeed I foster you a DCVS like git or mercurial.

Features
--------

lpbm is shipped with most of the features you want on a blog. Please keep in
mind that I broke most of the program on purpose, to enhance code base enough
so that I won't have to break it that much later when it's used by someone
other than me (hopefully).

 * You can write articles, have drafts and published articles.
 * You can have multiple authors on the blog and multiple authors on one
   article.
 * You can embed code easily in your articles, and it is colorized using
   pygments.

Things that are broken (on version 0.2, just a matter of time before it is back
on):

 * You can have categories, and put your articles into multiple categories.
 * An RSS feed is generated, so that your readers can follow you easily.

Road Map
--------

This project is in high development. This means that it can and probably will
break. Don't use it if you expect everything to work with no bug.

My main goal right now is to make it compatible with python 3, to clean the
code base and to document everything. My second goal is to add some automated
test (as much as possible). This will help maintain the current code breaking
on things that worked before.

When this will be done, it will be more easy to add new features. I am OK with
new ideas, but please keep in mind that this project should stay as tiny as
possible. Few features, only the necessary, but done nicely.
