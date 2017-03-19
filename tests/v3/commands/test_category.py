def test_category_list__no_category(lpbm_client):
    result = lpbm_client.run('category list', exit_code=0)
    assert result.output == 'No category\n'


def test_category_create__create_and_list(lpbm_client):
    result = lpbm_client.run('category create "Test"', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('category list', exit_code=0)
    assert result.output == 'Categories (1):\n  - Test\n'


def test_category_create__create_and_delete(lpbm_client):
    result = lpbm_client.run('category create "Test"', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('category delete "Test"', inp='y\n', exit_code=0)
    assert result.output == '''\
Are you sure you want to delete "Test"? [y/N]: y
Success!
'''

    result = lpbm_client.run('category delete "Test"', exit_code=1)
    assert result.output == 'Error: Category not found\n'


def test_category_create__create_with_unknown_parent(lpbm_client):
    result = lpbm_client.run('category create --parent "Foo" "Bar"', exit_code=1)
    assert result.output == 'Error: Parent category not found\n'

    result = lpbm_client.run('category create "Foo"', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('category create --parent "Foo" "Bar"', exit_code=0)
    assert result.output == 'Success!\n'
