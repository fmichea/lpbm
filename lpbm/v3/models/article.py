import lpbm.v3.lib.model as _mod

from lpbm.v3.models.author import Author
from lpbm.v3.models.category import Category


ARTICLE_SCHEMA = {
   _mod.Required('slugs'): {
       _mod.Required('current'): str,
       _mod.Optional('archive', default=list): [str],
   },
   _mod.Required('authors', default=list): [_mod.ModelRef(Author)],
   _mod.Optional('contributors', default=list): [_mod.ModelRef(Author)],
   _mod.Optional('category'): _mod.ModelRef(Category),
   _mod.Optional('tags', default=list): [str],
   _mod.Required('contents'): _mod.ExternalFileType(),
}


class Article(_mod.Model):
   __lpbm_config__ = {
       'schema': ARTICLE_SCHEMA,
       'filename_pattern': 'articles/{uuid}/article.yaml',
   }

   slug = _mod.ModelField('slugs.current')
   authors = _mod.ModelField('authors')
   category = _mod.ModelField('category')
   contents = _mod.ModelField('contents')


class ArticleEdit(_mod.Model):
    __lpbm_config__ = {
        'schema': {
            _mod.Optional('authors', default=list): [_mod.ModelRef(Author)],
            _mod.Required('patch'): _mod.ExternalFileType(),
        },
        'filename_pattern': Article.inline_model('drafts/{uuid}/draft.yaml'),
    }

    authors = _mod.ModelField('authors')
    draft = _mod.ModelField('draft')


def load_article_by_uid(uid):
    return SESSION.query(Article).filter(Article.uuid == uid).one_or_none()
