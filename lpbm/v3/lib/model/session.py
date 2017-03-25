import contextlib
import fcntl
import os

import yaml

import lpbm.v3.lib.path as lpath
from lpbm.v3.lib.model.errors import (
    ModelSessionBlogLockedError,
    ModelSessionReadOnlyError,
)
from lpbm.v3.lib.model.query import Query


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
        self.instances = dict()

    def initialize(self, rootdir):
        self.rootdir = rootdir
        self.begin()

    def begin(self):
        self.instances.clear()
        self._file_list = lpath.listdir(self.rootdir)
        self._to_delete_files = []

    def filter_filenames(self, filter_func):
        return [
            filename for filename in self._file_list
            if filter_func(filename)
        ]

    def add(self, *instances):
        for instance in instances:
            self.instances[instance.uuid] = instance

    def delete(self, *instances):
        for instance in instances:
            del self.instances[instance.uuid]
            self._to_delete_files.extend(instance.filenames())

    def query(self, model):
        return Query(model).with_session(self)

    def rollback(self):
        self.instances.clear()

    def commit(self):
        if self.mode != ModelSession.MODE_RW:
            raise ModelSessionReadOnlyError()
        # First we check that all instances are valid.
        for inst in self.instances.values():
            inst.validate()
        # We can save all the instances now.
        for inst in self.instances.values():
            self._model_save(inst)
        # Delete all the files to be deleted:
        for filename in self._to_delete_files:
            lpath.remove(self.in_blog_join(filename))
        # Clear all instances.
        self.instances.clear()
        # Clear the lists.
        self._to_delete_files = []
        return True

    def in_blog_join(self, *args):
        return os.path.join(self.rootdir, *args)

    def _model_save(self, inst):
        contents = yaml.safe_dump(inst.as_dict(), default_flow_style=False)

        filename = inst._model_filename()

        path = self.in_blog_join(filename)
        lpath.mkdir_p(os.path.dirname(path))

        with open(path, 'w') as fd:
            fd.write(contents)


SESSION = ModelSession()
