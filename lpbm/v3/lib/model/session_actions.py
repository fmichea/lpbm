import os

from lpbm.v3.lib import path as lpath


class CopyFileAction(object):
    def __init__(self, tmp_filename, dst_filename):
        self._tmp_filename = tmp_filename
        self._dst_filename = dst_filename

    def validate(self):
        # FIXME: check that we can indeed write to the destination file
        if not os.path.exists(self._tmp_filename):
            return False
        return True

    def do(self, session):
        fullpath = session.in_blog_join(self._dst_filename)
        lpath.mkdir_p(os.path.dirname(fullpath))
        os.rename(self._tmp_filename, fullpath)


class DeleteFileAction(object):
    def __init__(self, filename):
        self._filename = filename

    def validate(self):
        # FIXME: check access yo
        pass

    def do(self, session):
        lpath.remove(session.in_blog_join(self._filename))
