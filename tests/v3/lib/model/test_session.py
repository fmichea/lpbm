import re

import pytest

import lpbm.v3.lib.model as mmod
import lpbm.v3.lib.model.session as mod


def test_session__scoped_lock_cannot_be_locked_twice(test_tempdir):
    with mmod.scoped_session_ro(rootdir=test_tempdir) as session:
        with mod._scoped_lock(session):
            with pytest.raises(mmod.ModelSessionBlogLockedError):
                with mod._scoped_lock(session):
                    pass


def test_session__scoped_rw_can_be_double_scoped(test_tempdir):
    with mmod.scoped_session_rw(rootdir=test_tempdir) as session:
        with mmod.scoped_session_rw(session=session):
            pass


_FILE_LIST = [
    'a/b/c.yaml',
    'a/b/contents.txt',
    'a/c/b/wed.do',
    'a/c/contents.txt',
    'a/c/foo.yaml',
]


@pytest.mark.parametrize('pattern,result', [
    ('^.*$', _FILE_LIST),
    ('^.*\.yaml$', ['a/b/c.yaml', 'a/c/foo.yaml']),
    ('^a/b/.*$', ['a/b/c.yaml', 'a/b/contents.txt']),
])
def test_session__file_filtering_works(pattern, result):
    session = mod.ModelSession()
    session.file_list = _FILE_LIST

    func = lambda val: re.match(pattern, val) is not None
    assert sorted(session.filter_filenames(func)) == result


def test_session__scoped_rw_rollback_when_exception_happens(test_tempdir, monkeypatch):
    class obj(object):
        def __init__(self):
            self.call_count = 0

        def __call__(self, *a, **kw):
            self.call_count += 1

    rollback_func, commit_func = obj(), obj()

    with pytest.raises(Exception) as exc:
        with mmod.scoped_session_rw(rootdir=test_tempdir) as session:
            monkeypatch.setattr(session, 'commit', commit_func)
            monkeypatch.setattr(session, 'rollback', rollback_func)

            raise Exception('errrr')

    assert str(exc.value) == 'errrr'
    assert commit_func.call_count == 0
    assert rollback_func.call_count == 1


def test_session__cannot_commit_session_that_is_read_only(test_tempdir):
    with mmod.scoped_session_ro(rootdir=test_tempdir) as session:
        with pytest.raises(mmod.ModelSessionReadOnlyError):
            session.commit()
