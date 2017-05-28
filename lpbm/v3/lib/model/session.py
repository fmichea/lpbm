import contextlib
import fcntl
import os

import yaml

from lpbm.v3.lib import path as lpath
from lpbm.v3.lib.model.errors import (
    ModelSessionBlogLockedError,
    ModelSessionReadOnlyError,
)
from lpbm.v3.lib.model.query import Query
from lpbm.v3.lib.model.session_actions import DeleteFileAction


class _scoped_lock(object):
    def __init__(self, session):
        self._lock_path = os.path.join(session.rootdir, '.lock')

    def __enter__(self):
        self._fd = open(self._lock_path, 'w')
        try:
            fcntl.flock(self._fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except (OSError, IOError, BlockingIOError):
            self._fd.close()
            raise ModelSessionBlogLockedError()

    def __exit__(self, exc_type, exc_value, traceback):
        os.remove(self._lock_path)
        fcntl.flock(self._fd, fcntl.LOCK_UN)
        self._fd.close()


class _scoped_mode_change_rw(object):
    def __init__(self, session):
        self._session = session

    def __enter__(self):
        self._was_ro = (self._session.mode == ModelSession.MODE_RO)
        self._session.mode = ModelSession.MODE_RW
        return self._was_ro

    def __exit__(self, exc_type, exc_value, traceback):
        if self._was_ro:
            self._session.mode = ModelSession.MODE_RO


@contextlib.contextmanager
def scoped_session_rw(**options):
    result_func = options.get('result_func', lambda result: None)

    try:
        session = options['session']
    except KeyError:
        assert 'rootdir' in options

        session = ModelSession()
        session.initialize(options['rootdir'])

    with _scoped_mode_change_rw(session) as was_ro:
        if was_ro:
            with _scoped_lock(session):
                try:
                    yield session
                    result_func(session.commit())
                except:
                    session.rollback()
                    raise
        else:
            yield session


@contextlib.contextmanager
def scoped_session_ro(**options):
    try:
        session = options['session']
    except KeyError:
        assert 'rootdir' in options

        session = ModelSession()
        session.initialize(options['rootdir'])

    yield session
    session.rollback()


class ModelSession(object):
    MODE_RO, MODE_RW = 'ro', 'rw'

    def __init__(self):
        self.mode = ModelSession.MODE_RO

        self.file_list = set()
        self.instances = dict()
        self._commit_actions = []

    def initialize(self, rootdir):
        self.rootdir = rootdir
        self.begin()

    def begin(self):
        self.file_list = set(lpath.listdir(self.rootdir))
        self.instances.clear()
        self._commit_actions = []

    def filter_filenames(self, filter_func):
        return [
            filename for filename in self.file_list
            if filter_func(filename)
        ]

    def add_commit_action(self, act):
        self._commit_actions.append(act)

    def add(self, *instances):
        for instance in instances:
            self.instances[instance.uuid] = instance

    def delete(self, *instances):
        for instance in instances:
            del self.instances[instance.uuid]
            for filename in instance.filenames():
                self.add_commit_action(DeleteFileAction(filename))
                self.file_list.remove(filename)

    def query(self, model):
        return Query(model).with_session(self)

    def rollback(self):
        self.instances.clear()

    def commit(self):
        if self.mode != ModelSession.MODE_RW:
            raise ModelSessionReadOnlyError()
        # We can save all the instances now, this function adds commit actions
        # to the session. Instances may change (model ref checks), so we make a
        # copy.
        insts = list(self.instances.values())
        for inst in insts:
            inst.dump(self)
        # Do all the actions from the commit actions.
        for act in self._commit_actions:
            act.do(self)
        # Clear all instances.
        self.instances.clear()
        return True

    def in_blog_join(self, *args):
        return os.path.join(self.rootdir, *args)

    def is_in(self, *instances):
        for instance in instances:
            if instance.uuid in self.instances:
                continue

            inst = self.query(instance.__class__).get_or_none(instance.uuid)
            if inst is None:
                return False
        return True


SESSION = ModelSession()
