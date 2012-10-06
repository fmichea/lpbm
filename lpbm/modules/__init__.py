# -*- coding: utf-8 -*-

'''
A module is basically a command line sub-parser that helps manipulate a certain
object. Let say you want to manipulate articles, then a module is there to do
that stuff.

A module inherits from lpbm.module_loader.Module and implements abstract
methods of this class. It can have dependencies. All loading should be done in
load function, that will only be called if the module or one that depends on it
will be called. This helps not loading all the articles if you only want to add
a new author.

See :py:class:`lpbm.module_loader.Module` for more details on Module API.
'''
