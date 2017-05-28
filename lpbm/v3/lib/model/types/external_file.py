import shutil

from voluptuous import Optional as _Optional
from voluptuous import Required as _Required

from lpbm.v3.lib.model.session_actions import CopyFileAction
from lpbm.v3.lib.model.types.base import BaseType
from lpbm.v3.lib.tmp import tempfile


class ExternalFile(object):
    def __init__(self, filename, labels=[], path=None):
        self.labels = labels

        self.filename = filename
        self.tmp_filename = None
        self.path = None

    def open_filename(self, mode='r'):
        if mode not in ['r', 'w']:
            raise ValueError('FIXME: real exception')

        filename = self.tmp_filename or self.path
        if filename is None or mode == 'w':
            if self.tmp_filename is None:
                self.tmp_filename = tempfile()
            filename = self.tmp_filename

        return filename

    def copy_from(self, source):
        shutil.copyfile(source, self.open_filename('w'))


EXTERNAL_FILE_SCHEMA = {
    _Optional('label'): {
        _Optional('current'): str,
        _Optional('archive', default=list): [str],
    },
    _Required('filename'): str,
}


class ExternalFileType(BaseType):
    def __init__(self, *dirs):
        self._dirs = dirs

    def schema(self):
        return EXTERNAL_FILE_SCHEMA

    def filenames(self, owners, value):
        return owners.in_owner_join(value.filename)

    def load(self, session, owners, value):
        labels = None
        if 'label' in value:
            labels = value['label']['archive']
            labels.insert(0, value['label']['current'])

        return ExternalFile(
            value['filename'],
            labels=labels,
            path=owners.in_owner_join(value['filename'])
        )

    def dump(self, session, owners, value):
        # FIXME: make proper exceptions
        assert isinstance(value, ExternalFile)

        if value.tmp_filename is not None:
            session.add_commit_action(CopyFileAction(
                value.tmp_filename, owners.in_owner_join(value.filename)))


        result = {
            'filename': value.filename,
        }
        if value.labels:
            result['label'] = {
                'current': value.labels[0],
                'archive': value.labels[1:],
            }
        return result
