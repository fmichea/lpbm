import pytest

from lpbm.v3.commands import article as mod
from lpbm.v3.commands.root import getpass


@pytest.fixture(scope='function', autouse=True)
def getuser_auto_monkeypatch(monkeypatch):
    def f():
        raise OSError('wde')
    monkeypatch.setattr(getpass, 'getuser', f)


def test_article_list__no_article_exists(lpbm_client):
    result = lpbm_client.run('article list', exit_code=0)
    assert result.output == 'No article\n'


#@pytest.mark.parametrize('command', [
#    'article draft list',
#    'article draft create',
#    'article draft delete foo',
#    'article draft promote foo',
#])
#def test_article_draft__commands_require_cli_author(lpbm_client, command):
#    result = lpbm_client.run(command, exit_code=2)
#    assert 'Invalid value for --cli-author: mandatory cli author not defined' in result.output


@pytest.fixture()
def tester_author(lpbm_client):
    result = lpbm_client.run('author create tester', exit_code=0)
    assert 'Success' in result.output


#def test_article_draft__list_no_article(lpbm_client, tester_author):
#    result = lpbm_client.run('--cli-author tester article draft list', exit_code=0)
#    assert result.output == 'No draft by tester\n'


#@pytest.fixture()
#def awesome_draft(lpbm_client, tester_author, monkeypatch):
#    drafts_uuid = []
#
#    def edit(filename):
#        uuid = filename.rsplit('/', 1)[-1].rsplit('.', 1)[0]
#        assert len(uuid) == 36
#        drafts_uuid.append(uuid)
#
#        with open(filename, 'w') as fd:
#            fd.write('The awesome article\n===================\n\nBlag!')
#
#    monkeypatch.setattr(mod.editor, 'edit', edit)
#
#    # This creates a new draft.
#    result = lpbm_client.run('--cli-author tester article draft create', exit_code=0)
#    assert result.output == 'Draft "The awesome article" successfully created!\n'
#    assert len(drafts_uuid) == 1
#
#    return drafts_uuid[0]


#def test_article_draft__list_with_one_article_works(lpbm_client, awesome_draft):
#    # We can list this article.
#    result = lpbm_client.run('--cli-author tester article draft list', exit_code=0)
#    assert result.output == '''\
#Drafts by tester (1 draft(s)):
#  - {uuid}: The awesome article
#'''.format(uuid=awesome_draft)


#def test_article_draft__delete_of_article_works(lpbm_client, awesome_draft):
#    cmd = '--cli-author tester article draft delete {uuid}'
#    result = lpbm_client.run(cmd.format(uuid=awesome_draft), inp='y\n', exit_code=0)
#    assert result.output == '''\
#Draft for deletion:
#  - {uuid}: The awesome article
#Are you sure you want to delete this draft? [y/N]: y
#Success!
#'''.format(uuid=awesome_draft)
#
#    # list is empty now.
#    result = lpbm_client.run('--cli-author tester article draft list', exit_code=0)
#    assert result.output == 'No draft by tester\n'


#def test_article_draft__delete_can_be_cancelled(lpbm_client, awesome_draft):
#    cmd = '--cli-author tester article draft delete {uuid}'
#    result = lpbm_client.run(cmd.format(uuid=awesome_draft), inp='n\n', exit_code=1)
#    assert result.output == '''\
#Draft for deletion:
#  - {uuid}: The awesome article
#Are you sure you want to delete this draft? [y/N]: n
#Aborted!
#'''.format(uuid=awesome_draft)


#def test_article_draft__edit_of_content_and_title_works(lpbm_client, awesome_draft, monkeypatch):
#    def edit(filename):
#        with open(filename, 'w') as fd:
#            fd.write('The awesome article changed\n===========================\n\nGood Stuff.')
#
#    monkeypatch.setattr(mod.editor, 'edit', edit)
#
#    cmd = '--cli-author tester article draft edit {uuid}'
#    result = lpbm_client.run(cmd.format(uuid=awesome_draft), exit_code=0)
#    assert result.output == ''
#
#    result = lpbm_client.run('--cli-author tester article draft list', exit_code=0)
#    assert result.output == '''\
#Drafts by tester (1 draft(s)):
#  - {uuid}: The awesome article changed
#'''.format(uuid=awesome_draft)


#def test_article_draft_create__no_content_means_no_draft(lpbm_client, tester_author, monkeypatch):
#    def edit(filename):
#        pass
#
#    monkeypatch.setattr(mod.editor, 'edit', edit)
#
#    result = lpbm_client.run('--cli-author tester article draft create', exit_code=1)
#    assert result.output == 'Error: No draft created\n'


#@pytest.mark.parametrize('command', ['delete', 'edit', 'promote'])
#def test_article_draft__draft_not_found_commands(lpbm_client, tester_author, command):
#    command = '--cli-author tester article draft {cmd} wewdwed'.format(cmd=command)
#    result = lpbm_client.run(command, exit_code=1)
#    assert result.output == 'Error: draft not found\n'
