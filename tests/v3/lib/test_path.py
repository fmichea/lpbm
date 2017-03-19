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


def test_listdir_ignores_hidden_files_and_dirs(test_tempdir):
    for fname in [
        'a/b/.c/d',
        'a/.we',
        'b',
    ]:
        mod.mkdir_p(os.path.join(test_tempdir, fname))

    for fname in [
        'a/wde',
        'a/b/.c/wqdgt',
        'a/b/asdf',
        'b/.wedwed',
        'b/jdkdj',
    ]:
        with open(os.path.join(test_tempdir, fname), 'w') as fd:
            fd.write('')

    assert sorted(mod.listdir(test_tempdir)) == [
        'a/b/asdf',
        'a/wde',
        'b/jdkdj',
    ]
