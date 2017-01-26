import os

import lpbm.v3.lib.models as _mod


AUTHOR_EMAIL_LABELS = ('personal', 'business')


class AuthorTwitter(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Optional('handle'): str,
        },
    }

    handle = _mod.ModelField('handle')


class AuthorEmail(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Required('email'): _mod.Email(),
            _mod.Optional('label', default='personal'): _mod.Any(*AUTHOR_EMAIL_LABELS),
            _mod.Optional('is_primary', default=False): _mod.Boolean(),
        },
    }

    email = _mod.ModelField('email')
    label = _mod.ModelField('label')
    is_primary = _mod.ModelField('is_primary')


class Author(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Required('identity'): {
                _mod.Required('handles'): {
                    _mod.Required('current'): str,
                    'archive': list,
                },
                _mod.Optional('name', default=''): str,
                _mod.Optional('short-name', default=''): str,
            },
            _mod.Optional('email-accounts', default=list): [AuthorEmail],
            'social': {
                'twitter': AuthorTwitter,
            },
        },
        'filename_pattern': 'authors/{uuid}/author.yaml',
    }

    name = _mod.ModelField('identity.name')
    handle = _mod.ModelField('identity.handles.current')
    email_accounts = _mod.ModelField('email-accounts')


def load_author_by_handle(ctx, handle):
    authors = [
        author for author in Author.load_all()
        if author.handle == handle
    ]
    assert len(authors) < 2
    return authors[0] if authors else None
