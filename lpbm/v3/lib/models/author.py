import os

from voluptuous import Schema, Required, Optional, Email, Boolean, Any

from lpbm.v3.lib.models import Model, ModelField


AUTHOR_EMAIL_LABELS = ('personal', 'business')


AUTHOR_EMAIL_SCHEMA = Schema({
    Required('email'): Email(),
    Optional('label', default='personal'): Any(*AUTHOR_EMAIL_LABELS),
    Optional('is_primary', default=False): Boolean(),
})


AUTHOR_TWITTER_SCHEMA = Schema({
    Optional('handle'): str,
})


AUTHOR_SCHEMA = Schema({
    Required('identity'): {
        Required('handles'): {
            Required('current'): str,
            Optional('archive'): list,
        },
        Optional('name'): str,
        Optional('short-name'): str,
    },
    Optional('email-accounts'): [AUTHOR_EMAIL_SCHEMA],
    Optional('social'): {
        Optional('twitter'): AUTHOR_TWITTER_SCHEMA,
    },
})


class AuthorTwitter(Model):
    __lpbm_config__ = {
        'schema': AUTHOR_TWITTER_SCHEMA,
    }

    handle = ModelField('handle')


class AuthorEmail(Model):
    __lpbm_config__ = {
        'schema': AUTHOR_EMAIL_SCHEMA,
    }

    email = ModelField('email')
    label = ModelField('label')
    is_primary = ModelField('is_primary')


class Author(Model):
    __lpbm_config__ = {
        'schema': AUTHOR_SCHEMA,
        'filename_pattern': 'authors/{uuid}/author.yaml',
    }

    name = ModelField('identity.name', default=None)
    handle = ModelField('identity.handles.current')

    email_accounts = ModelField(
        'email-accounts', default=lambda: [], value_type=AuthorEmail)


def load_author_by_handle(ctx, handle):
    authors = [
        author for author in Author.load_all()
        if author.handle == handle
    ]
    assert len(authors) < 2
    return authors[0] if authors else None
