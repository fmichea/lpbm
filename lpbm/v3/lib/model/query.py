import re

import yaml

from lpbm.v3.lib.model.uuid import UUID_RE_S, UUID_RE
from lpbm.v3.lib.model.errors import (
    ModelQueryInvalidCriterionError,
    ModelQueryNoObjectFoundError,
    ModelQueryNoParentError,
    ModelQueryParentAlreadySetError,
    ModelQueryParentWrongTypeError,
    ModelQueryTooManyObjectsError,
)
from lpbm.v3.lib.model.field import ModelField
from lpbm.v3.lib.model.field_bool_op import ModelFieldBoolOp, and_


class Query(object):
    def __init__(self, model):
        self._model = model
        self._session = None
        self._parent = None
        self._filter_criteria = []
        self._order_by_criteria = []

        self._filename_uuids = {
            parent_uuid: UUID_RE_S
            for parent_uuid in model._parents_uuids()
        }
        self._filename_uuids['uuid'] = UUID_RE_S

    def with_session(self, session):
        self._session = session
        return self

    def filter(self, *criteria):
        for criterion in criteria:
            if not isinstance(criterion, ModelFieldBoolOp):
                raise ModelQueryInvalidCriterionError()
        self._filter_criteria.extend(criteria)
        return self

    def order_by(self, *criteria):
        for criterion in criteria:
            if not isinstance(criterion, ModelField):
                raise ModelQueryInvalidCriterionError()
        self._order_by_criteria.extend(criteria)
        return self

    def parent(self, parent):
        if self._parent is not None:
            raise ModelQueryParentAlreadySetError()

        parent_cls = self._model._filename_pattern('parent')
        if parent_cls is None:
            raise ModelQueryNoParentError()

        if type(parent) is not parent_cls['class']:
            raise ModelQueryParentWrongTypeError()

        self._parent = parent

        uuids = parent._parents_refs_uuid()
        uuids['{0}_uuid'.format(parent_cls['name'])] = parent.uuid
        self._filename_uuids.update(uuids)

        return self

    def get(self, uuid, **uuids):
        uuids.update({'uuid': uuid})
        self._filename_uuids.update(uuids)
        return self.one()

    def all(self):
        full_pattern = self._model._filename_pattern('full_pattern')
        # First build the path with known uuids.
        path = full_pattern.format(**self._filename_uuids)
        filename = re.compile('^{0}$'.format(path))

        def filter_func(x):
            return filename.match(x) is not None

        filenames = self._session.filter_filenames(filter_func)
        # Load all objects from their file.
        result = [
            self._model_load_from_file(filename)
            for filename in filenames
        ]
        # Filtering objects based on the filters.
        if self._filter_criteria:
            filter_func = and_(*self._filter_criteria)
            result = [model for model in result if filter_func.test(model)]
        # Ordering the objects.
        if self._order_by_criteria:
            def keyfunc(inst):
                return tuple(field.get(inst) for field in self._order_by_criteria)

            result = sorted(result, key=keyfunc)
        # All good.
        return result

    def one(self):
        model = self.one_or_none()
        if model is None:
            raise ModelQueryNoObjectFoundError()
        return model

    def one_or_none(self):
        models = self.all()
        if 2 <= len(models):
            raise ModelQueryTooManyObjectsError()
        if not models:
            return None
        return models[0]

    def count(self):
        return len(self.all())

    def first(self):
        model = self.first_or_none()
        if model is None:
            raise ModelQueryNoObjectFoundError()
        return model

    def first_or_none(self):
        models = self.all()
        if not models:
            return None
        return models[0]

    def delete(self):
        models = self.all()
        self._session.delete(*models)
        return len(models)

    def _model_load_from_file(self, filename):
        # Extract UUID from filename.
        suffix_len = len(self._model._filename_pattern('suffix'))
        uuid = filename[:-suffix_len][:-1][-36:]
        assert UUID_RE.match(uuid) is not None
        try:
            return self._session.instances[uuid]
        except KeyError:
            with open(self._session.in_blog_join(filename)) as fd:
                data = yaml.safe_load(fd.read())

            data = self._model._schema()(data)

            obj = self._model(data=data, session=self._session, parent=self._parent)
            self._session.instances[obj.uuid] = obj
            return obj
