import os

from contextlib import contextmanager

from lpbm.v3.lib.model.base import model_name_id


class OwnerTracker:
    def __init__(self):
        self._owners = []

    def clean_repr(self):
        return ' > '.join(model_name_id(owner) for owner in self._owners)

    @contextmanager
    def wrap(self, owner):
        self._owners.append(owner)
        try:
            yield
        finally:
            self._owners.pop()

    def _dirname(self):
        assert self._owners[0].is_in_file_model()
        return os.path.dirname(self._owners[0]._model_filename())

    def in_owner_join(self, *args):
        return os.path.join(self._dirname(), *args)
