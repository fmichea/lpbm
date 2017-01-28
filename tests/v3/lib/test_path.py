import os

import lpbm.v3.lib.path as mod


def test_remove_works_on_file(test_tempdir):
    fname = os.path.join(test_tempdir, 'foo.txt')

    with open(fname, 'w') as fd:
        fd.write('fooooo')
    mod.remove(fname)


def test_remove_works_on_directory(test_tempdir):
    fname = os.path.join(test_tempdir, 'foo')

    mod.mkdir_p(fname)
    mod.remove(fname)


def test_remove_warns_if_other_file_type(test_tempdir):
    fname = os.path.join(test_tempdir, 'foo')
    mod.remove(fname)
