import click

from lpbm.v3.commands.root import command_with_commit, main_command
from lpbm.v3.lib.model import SESSION
from lpbm.v3.models.author import (
    AUTHOR_EMAIL_LABELS,
    Author,
    AuthorEmail,
    load_author_by_uid,
)


@main_command.group('author')
def author():
    """author management commands"""


@author.command('list')
def author__list():
    """list all the blog authors"""
    authors = SESSION.query(Author).all()

    if authors:
        click.echo('Authors ({0}):'.format(len(authors)))
        for author in authors:
            click.echo('  - {handle}'.format(handle=author.handle))
    else:
        click.echo('No authors')


@author.command('create')
@click.argument('handle')
@click.pass_context
@command_with_commit()
def author__create(ctx, handle):
    """create a new author"""
    author = load_author_by_uid(handle)
    if author is not None:
        raise click.ClickException('Author already exists.')

    author = Author()
    author.handle = handle

    SESSION.add(author)


@author.command('delete')
@click.argument('uid')
@click.pass_context
@command_with_commit()
def author__delete(ctx, uid):
    """delete an author by handle"""
    author = load_author_by_uid(uid)
    if author is None:
        raise click.ClickException('Author does not exist.')

    message = 'Are you sure you want to delete {handle}?'
    click.confirm(message.format(handle=author.handle), abort=True)

    SESSION.delete(author)


@author.command('info')
@click.argument('uid')
@click.pass_context
def author__info(ctx, uid):
    """get information about author"""
    author = load_author_by_uid(uid)
    if author is None:
        raise click.ClickException('Author does not exist.')

    click.echo('Handle: {0}'.format(author.handle))

    if author.name != '':
        click.echo('Name: {0}'.format(author.name))

    if author.email_accounts:
        click.echo('Emails:')
        for author_email in author.email_accounts:
            click.echo('  - {primary} [{label}] {email}'.format(
                primary=('*' if author_email.is_primary else ' '),
                label=author_email.label,
                email=author_email.email,
            ))


@author.group('edit')
@click.argument('uid')
@click.pass_context
def author__edit(ctx, uid):
    """edit author information"""
    ctx.obj['author'] = load_author_by_uid(uid)
    if ctx.obj['author'] is None:
        raise click.ClickException('Author does not exist.')


@author__edit.command('set-name')
@click.argument('name')
@click.pass_context
@command_with_commit()
def author__edit__set_name(ctx, name):
    """change the name of an author"""
    ctx.obj['author'].name = name


@author__edit.group('email')
def author__edit__email():
    """edit email for author"""
    pass


@author__edit__email.command('add')
@click.argument('email')
@click.pass_context
@command_with_commit()
def author__edit__email__add(ctx, email):
    """add email for author"""
    author_emails = ctx.obj['author'].email_accounts

    if any(author_email.email == email for author_email in author_emails):
        raise click.ClickException('Email already exists.')

    author_email = AuthorEmail(parent=ctx.obj['author'])
    author_email.email = email

    SESSION.add(author_email)


@author__edit__email.group('edit')
@click.argument('email')
@click.pass_context
def author__edit__email__edit(ctx, email):
    ctx.obj['author-emails'] = ctx.obj['author'].email_accounts

    authors = [
        author_email for author_email in ctx.obj['author-emails']
        if author_email.email == email
    ]
    if len(authors) != 1:
        raise click.ClickException('Email does not exist.')
    ctx.obj['author-emails-selected'] = authors[0]


@author__edit__email__edit.command('set-primary')
@click.pass_context
@command_with_commit()
def author__edit__email__edit__set_primary(ctx):
    """makes email primary email for author"""
    for author_email in ctx.obj['author-emails']:
        author_email.is_primary = False

    ctx.obj['author-emails-selected'].is_primary = True


@author__edit__email__edit.command('set-label')
@click.argument('label')
@click.pass_context
@command_with_commit()
def author__edit__email__edit__set_label(ctx, label):
    """sets the label for email (personal, business, ...)"""
    if label not in AUTHOR_EMAIL_LABELS:
        msg = 'not a valid label value. Values available: {0}'
        msg = msg.format(', '.join(AUTHOR_EMAIL_LABELS))
        raise click.ClickException(msg)

    ctx.obj['author-emails-selected'].label = label


@author__edit__email.command('delete')
@click.argument('email')
@click.pass_context
@command_with_commit()
def author__edit__email__delete(ctx, email):
    """delete email from author"""
    author = ctx.obj['author']

    author_emails = (  # noqa: E131
        SESSION.query(AuthorEmail)
            .parent(author)
            .filter(AuthorEmail.email == email)
            .all()
    )

    if not author_emails:
        raise click.ClickException('Email does not exist.')

    message = 'Are you sure you want to delete {email} from {handle}?'
    click.confirm(message.format(handle=author.handle, email=email), abort=True)

    SESSION.delete(author_emails[0])
