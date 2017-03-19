import lpbm.v3.lib.model as _mod


class Category(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Required('name'): str,
            'parent-category': _mod.ModelRef('Category'),
        },
        'filename_pattern': 'categories/{uuid}/category.yaml',
    }

    name = _mod.ModelField('name')
    parent_category = _mod.ModelField('parent-category')


def load_category_by_uid(uid):
    return _mod.SESSION.query(Category).filter(
        _mod.or_(
            Category.uuid == uid,
            Category.name == uid,
        )
    ).one_or_none()
