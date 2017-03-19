import click

from lpbm.v3.commands.root import command_with_commit, main_command
from lpbm.v3.lib.model import SESSION
from lpbm.v3.models.category import Category, load_category_by_uid


@main_command.group('category')
def category():
    """category management commands"""


@category.command('list')
def category__list():
    """list all the blog categories"""
    categories = SESSION.query(Category).all()

    if categories:
        click.echo('Categories ({0}):'.format(len(categories)))
        for category in categories:
            click.echo('  - {name}'.format(name=category.name))
    else:
        click.echo('No category')


@category.command('create')
@click.option('-p', '--parent', metavar='parent_uid', help='parent category')
@click.argument('name')
@command_with_commit()
def category__create(parent, name):
    parent_uid, parent = parent, None

    if parent_uid:
        parent = load_category_by_uid(parent_uid)
        if parent is None:
            raise click.ClickException('Parent category not found')

    category = Category()
    if parent is not None:
        category.parent_category = parent
    category.name = name

    SESSION.add(category)


@category.command('delete')
@click.argument('uid')
@command_with_commit()
def category__delete(uid):
    category = load_category_by_uid(uid)

    if category is None:
        raise click.ClickException('Category not found')

    msg = 'Are you sure you want to delete "{cat}"?'.format(cat=category.name)
    click.confirm(msg, abort=True)

    SESSION.delete(category)
