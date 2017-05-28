import tempfile as _tempfile
import shutil

from contextlib import contextmanager


_TMP_SESSION_DIR = None


class TmpSession(object):
    def __enter__(self):
        global _TMP_SESSION_DIR
        _TMP_SESSION_DIR = _tempfile.mkdtemp(prefix='tmp-lpbm-session-')

    def __exit__(self, *args):
        global _TMP_SESSION_DIR
        shutil.rmtree(_TMP_SESSION_DIR)
        _TMP_SESSION_DIR = None


def tempfile():
    return _tempfile.mkstemp(dir=_TMP_SESSION_DIR)[1]
