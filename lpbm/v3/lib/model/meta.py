import os
import re

from voluptuous import Required

from lpbm.v3.lib import path as lpath
from lpbm.v3.lib.model import data as lmdata
from lpbm.v3.lib.model.base import BaseModel
from lpbm.v3.lib.model.errors import ModelTypeError
from lpbm.v3.lib.model.field import ModelField
from lpbm.v3.lib.model.schema import ModelSchema as _ModelSchema
from lpbm.v3.lib.model.uuid import UUID as _UUID
from lpbm.v3.lib.model.uuid import new_uuid as _new_uuid

_CLSNAME_RE = re.compile('([A-Z][a-z]*)')


class ModelMeta(type):
    CONFIG_ATTR = '__lpbm_config__'

    def __new__(cls, name, bases, namespace, **kw):
        # Model names must be unique for ModelRef to work.
        if name in lmdata.MODEL_NAME_TO_CLASS:
            err = 'Invalid model name {clsname} used for two models'
            raise ModelTypeError(err.format(clsname=name))

        # Base model is the class all models inherit from, we do not want to
        # apply all of the meta actions on it.
        is_base_model = (name == 'Model' and bases == (BaseModel,))

        # All the attributes
        kw = dict(namespace)

        # Model must provide configuration with regards to the model's schema
        # in an attribute with a specific name.
        if (
            ModelMeta.CONFIG_ATTR not in kw or
            not isinstance(kw[ModelMeta.CONFIG_ATTR], dict)
        ):
            err = 'model {clsname} must provide dict __lpbm_config__'
            raise ModelTypeError(err.format(clsname=name))

        cfg = kw[ModelMeta.CONFIG_ATTR]

        # Only the base class for all models does not define a schema. Every
        # other class must define one.
        schema = cfg.get('schema')
        if schema is None:
            err = 'model {clsname} must provide a data schema in {attr}'
            raise ModelTypeError(err.format(clsname=name, attr=ModelMeta.CONFIG_ATTR))

        # Models must have a schema which validates the data they contain.
        if not isinstance(schema, dict):
            err = 'model {clsname} must provide data schema as a dict'
            raise ModelTypeError(err.format(clsname=name))

        # Only BaseModel can define the uuid or parent attribute (a property).
        if not is_base_model:
            for attr_name in 'uuid,parent'.split(','):
                if attr_name in kw:
                    err = 'model {clsname} cannot have a {attr_name} attribute'
                    raise ModelTypeError(err.format(clsname=name, attr_name=attr_name))

        filename_pattern = cfg.get('filename_pattern')

        # If filename_pattern is defined, Model can be referenced through a
        # file, and will be uniquely identified using a UUID4.
        if filename_pattern is not None:
            schema[Required('uuid', default=_new_uuid)] = _UUID
            kw['uuid'] = ModelField('uuid', read_only=True)

            def _split_filename_pattern(ptrn):
                # filename_pattern must contain '{uuid}' where the model uuid
                # will be used in the filename. We pre-treat model filename
                # pattern so every information is accessible easily.
                parts = lpath.full_split(ptrn)
                root, part = '', parts.pop()
                while part != '{uuid}':
                    root = os.path.join(root, part)
                    part = parts.pop()
                assert len(parts) == 1
                return root, parts[0]

            if isinstance(filename_pattern, str):
                prefix, suffix = _split_filename_pattern(filename_pattern)

                cfg['filename_pattern'] = {
                    'full_pattern': filename_pattern,
                    'prefix': prefix,
                    'suffix': suffix,
                    'parent': None,
                }

            @classmethod
            def inline_model(cls, pth):
                clsname = [it for it in _CLSNAME_RE.split(cls.__name__) if it]
                clsname = '_'.join(clsname).lower()

                prefix, suffix = _split_filename_pattern(pth)
                prefix = '{0}/{{{1}_uuid}}/{1}'.format(
                    cls._filename_pattern('prefix'), clsname, prefix)

                return {
                    'full_pattern': '{0}/{{uuid}}/{1}'.format(prefix, suffix),
                    'prefix': prefix,
                    'suffix': suffix,
                    'parent': {'name': clsname, 'class': cls},
                }

            kw['inline_model'] = inline_model

        # If at this point we have not defined uuid, we define it as None.
        kw.setdefault('uuid', None)

        # Modified schema is saved to the model configuration.
        cfg['schema'] = _ModelSchema(schema)

        # Create the class and save it in our name -> class mapping.
        res = super().__new__(cls, name, bases, kw)
        lmdata.MODEL_NAME_TO_CLASS[name] = res

        return res
