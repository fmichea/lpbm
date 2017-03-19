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
