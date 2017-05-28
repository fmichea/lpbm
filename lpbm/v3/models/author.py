import os

from lpbm.v3.lib import model as _mod
from lpbm.v3.lib.model import SESSION

AUTHOR_EMAIL_LABELS = ('personal', 'business')


class AuthorTwitter(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Optional('handle'): str,
        },
    }

    handle = _mod.ModelField('handle')


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
            'social': {
                'twitter': AuthorTwitter,
            },
        },
        'filename_pattern': 'authors/{uuid}/author.yaml',
    }

    name = _mod.ModelField('identity.name')
    handle = _mod.ModelField('identity.handles.current')

    def display_name(self):
        if self.name:
            return self.name
        return self.handle

    @property
    def email_accounts(self):
        return (  # noqa: E131
            SESSION.query(AuthorEmail)
                .parent(self)
                .order_by(AuthorEmail.email)
                .all()
        )

    def drafts(self):
        drafts, drafts_dir = [], self.in_model_join('.drafts')
        if os.path.exists(drafts_dir):
            for draft_filename in os.listdir(drafts_dir):
                drafts.append({
                    'uuid': draft_filename.rsplit('.', 1)[0],
                    'path': os.path.join(drafts_dir, draft_filename),
                })
        return drafts

    def draft_from_uuid(self, uuid):
        draft = None
        for draft_tmp in self.drafts():
            if draft_tmp['uuid'] == uuid:
                draft = draft_tmp
                break
        return draft


class AuthorEmail(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Required('email'): _mod.Email(),
            _mod.Optional('label', default='personal'): _mod.Any(*AUTHOR_EMAIL_LABELS),
            _mod.Optional('is_primary', default=False): _mod.Boolean(),
        },
        'filename_pattern': Author.inline_model('emails/{uuid}/email.yaml'),
    }

    email = _mod.ModelField('email')
    label = _mod.ModelField('label')
    is_primary = _mod.ModelField('is_primary')


def load_author_by_uid(uid):
    return (
        SESSION.query(Author).filter(_mod.or_(
            Author.uuid == uid,
            Author.handle == uid,
        )).one_or_none()
    )
