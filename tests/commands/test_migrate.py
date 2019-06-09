import os

import pytest

import lpbm.modules.migrate as mod


def _check_file_exists(root, filename):
    assert os.path.exists(os.path.join(root, filename)), 'missing filename ' + filename


def _check_file_contains(root, filename, values):
    _check_file_exists(root, filename)

    with open(os.path.join(root, filename)) as fd:
        contents = fd.read()

    for value in values:
        assert value in contents


def _check_mandatory_files(root):
    for filename in [
        'Gemfile',
        'Gemfile.lock',
        '_config.yml',
        'index.md',
        'rssfeed.xml',
    ]:
        _check_file_exists(root, filename)


def _check_test_blog_1(root):
    _check_file_contains(root, '_authors/alex.md', [
        'Alex Smith',
        'alex@example.com',
    ])
    _check_file_contains(root, '_authors/aiden.md', [
        'Aiden Johnson',
        'aiden@example.com',
    ])

    _check_file_contains(root, '_drafts/2019-06-16-second-post-best-post.md', [
        'title: "Second Post Best Post"',
        'This is a second post with multiple authors, yay!',
        '/articles/1-second-post-best-post.html',
        'authors: [aiden,alex,]',
        'categories: ["Main Category 1 > Sub Category 1"]',
    ])

    _check_file_contains(root, '_posts/2019-06-09-some-cool-post.md', [
        'title: "Some Cool Post"',
        'authors: [alex,]',
        'categories: ["Main Category 1 > Sub Category 2"]',
        '/articles/0-some-cool-post.html',
        'This is some cool first post for my blog!',
    ])


@pytest.mark.parametrize(('blog_name', 'check_function'), [
    ('test-blog-1', _check_test_blog_1),
])
def test_full_migration(command_caller, monkeypatch, test_result_tempdir, blog_name, check_function):
    monkeypatch.setattr(mod.ltools, 'ask_sure', lambda *a, **kw: True)
    command_caller(['migrate'], blog=blog_name)

    _check_mandatory_files(test_result_tempdir)
    check_function(test_result_tempdir)
