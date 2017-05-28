import os
import subprocess
import threading

import click

from watchdog.events import (
    FileCreatedEvent,
    FileModifiedEvent,
    DirModifiedEvent,
    FileSystemEventHandler,
)
from watchdog.observers import Observer

from lpbm.v3.commands.root import (
    command_with_cli_author,
    command_with_commit,
    main_command,
)
from lpbm.v3.lib import editor
from lpbm.v3.lib.markdown import extract_title
from lpbm.v3.lib.model import scoped_session_rw, SESSION
from lpbm.v3.lib.path import mkdir_p
from lpbm.v3.lib.slugify import slugify
from lpbm.v3.lib.uuid import new_uuid
from lpbm.v3.models.article import (
    Article,
    ArticleEdit,
    load_article_by_uid,
)
from lpbm.v3.lib.model.types.external_file import ExternalFile


@main_command.group('article')
def article():
    """article manageemnt commands"""


@article.command('list')
def article__list():
    """list all the blog articles"""
    articles = SESSION.query(Article).all()

    if articles:
        click.echo('Articles ({0}):'.format(len(articles)))
        for article in articles:
            click.echo('  - {title}'.format(title='wed'))
    else:
        click.echo('No article')


@article.command('create')
@command_with_cli_author()
@click.pass_context
def article__create(ctx):
    tmp_uuid = new_uuid()

    path = os.path.join(
        ctx.obj['exec-path'],
        '.tmp',
        'article-new-{uuid}'.format(uuid=tmp_uuid),
    )
    mkdir_p(path)

    article_path = os.path.join(path, 'article.markdown')

    class EditorThread(threading.Thread):
        def run(self):
            editor.edit(article_path)

    editor_thread = EditorThread()
    editor_thread.start()

    class FSEventHandler(FileSystemEventHandler):
        def __init__(self):
            self._article_uuid = None

        def on_any_event(self, event):
            if (
                isinstance(event, (FileCreatedEvent, FileModifiedEvent)) and
                event.src_path == article_path
            ):
                with scoped_session_rw(rootdir=ctx.obj['exec-path']) as session:
                    if self._article_uuid is None:
                        article = Article()
                        self._article_uuid = article.uuid

                        article.authors.append(ctx.obj['cli-author'])
                        article.slug = extract_title(article_path)

                        article.contents = ExternalFile('article.markdown')
                        article.contents.copy_from(article_path)

                        session.add(article)
                    else:
                        article = session.query(Article).get(self._article_uuid)
                        article.contents.copy_from(article_path)
                return

            if isinstance(event, DirModifiedEvent) and event.src_path == path:
                return

    event_handler = FSEventHandler()

    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()

    editor_thread.join()

    observer.stop()
    observer.join()

#    article_uuid_path = os.path.join(path, 'article-uuid')
#
#    if os.path.exists(article_uuid_path):
#        return
#
#    class result(object):
#        def __init__(self):
#            self.result = False
#
#        def __call__(self, result):
#            self.result = result
#
#    result_func = result()
#
#    with scoped_session_rw(rootdir=ctx.obj['exec-path'], result_func=result_func) as session:
#        article = Article()
#        article.contents = ExternalFile(article, filename='article.markdown')
#
#        session.add(article)
#
#    if result_func.result:
#        click.secho('Success!', fg='green')
#        click.echo('To edit: lpbm-v3 article edit create {article_uuid}'.format(
#            article_uuid=article.uuid))
#    else:
#        click.secho('Failure', fg='red')


@article.group('edit')
def article__edit():
    pass


#@article.group('draft')
#def article__draft():
#    pass
#
#
#@article__draft.command('list')
#@command_with_cli_author()
#@click.pass_context
#def article__draft__list(ctx):
#    drafts = ctx.obj['cli-author'].drafts()
#
#    if drafts:
#        click.echo('Drafts by {author_name} ({count} draft(s)):'.format(
#            author_name=ctx.obj['cli-author'].display_name(),
#            count=len(drafts)
#        ))
#        for draft in drafts:
#            click.echo('  - {uuid}: {title}'.format(
#                uuid=draft['uuid'], title=extract_title(draft['path'])))
#    else:
#        click.echo('No draft by {author_name}'.format(
#            author_name=ctx.obj['cli-author'].display_name(),
#        ))
#
#
#@article__draft.command('create')
#@click.option('--format', default='markdown', type=click.Choice(['markdown']),
#              help='format the article will be written in')
#@command_with_cli_author()
#@click.pass_context
#def article__draft__create(ctx, format):
#    draft_dirs = ctx.obj['cli-author'].in_model_join('.drafts')
#    mkdir_p(draft_dirs)
#
#    draft_path = os.path.join(draft_dirs, '{0}.{1}'.format(new_uuid(), format))
#    editor.edit(draft_path)
#
#    if os.path.exists(draft_path):
#        click.secho('Draft "{title}" successfully created!'.format(
#            title=extract_title(draft_path)), fg='green')
#    else:
#        raise click.ClickException('No draft created')
#
#
#@article__draft.command('edit')
#@click.argument('uuid', required=True)
#@command_with_cli_author()
#@click.pass_context
#def article__draft__edit(ctx, uuid):
#    draft = ctx.obj['cli-author'].draft_from_uuid(uuid)
#
#    if draft is None:
#        raise click.ClickException('draft not found')
#
#    editor.edit(draft['path'])
#
#
#@article__draft.command('delete')
#@click.argument('uuid', required=True)
#@command_with_cli_author()
#@click.pass_context
#def article__draft__delete(ctx, uuid):
#    draft = ctx.obj['cli-author'].draft_from_uuid(uuid)
#
#    if draft is None:
#        raise click.ClickException('draft not found')
#
#    click.echo('Draft for deletion:')
#    click.echo('  - {uuid}: {title}'.format(
#        uuid=draft['uuid'], title=extract_title(draft['path'])))
#
#    click.confirm('Are you sure you want to delete this draft?', abort=True)
#
#    os.remove(draft['path'])
#
#    click.secho('Success!', fg='green')
#
#
#@article__draft.command('promote')
#@click.argument('uuid', required=True)
#@command_with_cli_author()
#@click.pass_context
#def article__draft__promote(ctx, uuid):
#    draft = ctx.obj['cli-author'].draft_from_uuid(uuid)
#
#    if draft is None:
#        raise click.ClickException('draft not found')
#
#    title = extract_title(draft['path'])
#
#    click.echo('Draft to promote:')
#    click.echo('  - {uuid}: {title}'.format(uuid=draft['uuid'], title=title))
#
#    click.confirm('Are you sure you want to promote those drafts?', abort=True)
#
#    with scoped_session_rw(rootdir=ctx.obj['exec-path']) as session:
#        article = Article()
#        article.authors.append(ctx['cli-author'])
#        article.slug = slugify(title)
#
#        session.add(article)
