def test_author_list__no_author_exists(lpbm_client):
    result = lpbm_client.run('author list', exit_code=0)
    assert result.output == 'No authors\n'


def test_author_create__create_and_list(lpbm_client):
    result = lpbm_client.run('author create john', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author list', exit_code=0)
    assert result.output == 'Authors (1):\n  - john\n'


def test_author_create__cannot_create_author_already_exists(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author create jane', exit_code=1)
    assert result.output == 'Error: Author already exists.\n'


def test_author_delete__unknown_author_fails(lpbm_client):
    result = lpbm_client.run('author delete john', exit_code=1)
    assert result.output == 'Error: Author does not exist.\n'


def test_author_delete__no_author_after_delete(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author delete jane', inp='y\n', exit_code=0)
    assert result.output == '''\
Are you sure you want to delete jane? [y/N]: y
Success!
'''

    result = lpbm_client.run('author list', exit_code=0)
    assert result.output == 'No authors\n'


def test_author__author_info_unknown_author_fails(lpbm_client):
    result = lpbm_client.run('author info john', exit_code=1)
    assert result.output == 'Error: Author does not exist.\n'


def test_author__author_info_shows_handle(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info jane', exit_code=0)
    assert result.output == 'Handle: jane\n'


def test_author__author_edit_unknown_author_fails(lpbm_client):
    result = lpbm_client.run('author edit john set-name "John Doe"', exit_code=1)
    assert result.output == 'Error: Author does not exist.\n'


def test_author__author_edit_add_name(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author edit jane set-name "Jane Doe"', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info jane', exit_code=0)
    assert result.output == 'Handle: jane\nName: Jane Doe\n'


def test_author__author_edit_add_email(lpbm_client):
    result = lpbm_client.run('author create john', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit john email add john@example.com',
        exit_code=0,
    )
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info john', exit_code=0)
    assert result.output == '''\
Handle: john
Emails:
  -   [personal] john@example.com
'''


def test_author__author_edit_add_email_twice_does_not_work(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email add jane@example.com', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email add jane@example.com', exit_code=1)
    assert result.output == 'Error: Email already exists.\n'


def test_author__author_edit_email_set_primary_with_one_email(lpbm_client):
    result = lpbm_client.run('author create john', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit john email add john@example.com', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit john email edit john@example.com set-primary',
        exit_code=0,
    )
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info john', exit_code=0)
    assert result.output == '''\
Handle: john
Emails:
  - * [personal] john@example.com
'''


def test_author__author_edit_email_set_primary_multiple_emails_one_primary(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email add jane@example.com', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email add jane@work.example.com', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email edit jane@example.com set-primary',
        exit_code=0,
    )
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info jane', exit_code=0)
    assert result.output == '''\
Handle: jane
Emails:
  - * [personal] jane@example.com
  -   [personal] jane@work.example.com
'''

    result = lpbm_client.run(
        'author edit jane email edit jane@work.example.com set-primary',
        exit_code=0,
    )
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info jane', exit_code=0)
    assert result.output == '''\
Handle: jane
Emails:
  -   [personal] jane@example.com
  - * [personal] jane@work.example.com
'''


def test_author__author_edit_set_label_proper_value(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email add jane@example.com', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email edit jane@example.com set-label business',
        exit_code=0,
    )
    assert result.output == 'Success!\n'

    result = lpbm_client.run('author info jane', exit_code=0)
    assert result.output == '''\
Handle: jane
Emails:
  -   [business] jane@example.com
'''


def test_author__author_edit_label_with_wrong_value(lpbm_client):
    result = lpbm_client.run('author create john', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit john email add john@example.com',
        exit_code=0,
    )
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit john email edit john@example.com set-label unknown',
        exit_code=1,
    )
    assert result.output == '''\
Error: not a valid label value. Values available: personal, business
'''


def test_author__author_email_can_be_deleted(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email add jane@example.com', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email delete jane@example.com',
        exit_code=0,
        inp='y\n',
    )
    assert result.output == '''\
Are you sure you want to delete jane@example.com from jane? [y/N]: y
Success!
'''

    result = lpbm_client.run('author info jane', exit_code=0)
    assert result.output == 'Handle: jane\n'


def test_author__author_edit_unknown_email(lpbm_client):
    result = lpbm_client.run('author create john', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit john email edit john@example.com set-label unknown',
        exit_code=1,
    )
    assert result.output == 'Error: Email does not exist.\n'


def test_author__author_delete_unexisting_email(lpbm_client):
    result = lpbm_client.run('author create jane', exit_code=0)
    assert result.output == 'Success!\n'

    result = lpbm_client.run(
        'author edit jane email delete jane@example.com',
        exit_code=1,
    )
    assert result.output == 'Error: Email does not exist.\n'
