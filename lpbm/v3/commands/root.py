import click
import getpass

from lpbm.v3.lib.model import SESSION, scoped_session_rw
from lpbm.v3.lib.tmp import TmpSession
from lpbm.v3.meta.version import __version__
from lpbm.v3.models.author import load_author_by_uid


class _tmp_init_command(object):
    def __call__(self, func):
        def wrapper(*a, **kw):
            with TmpSession():
                return func(*a, **kw)
        return wrapper


@click.group()
@click.version_option(version=__version__)
@click.option('-P', '--exec-path', default='.',
              type=click.Path(exists=True, resolve_path=True),
              help='path to the blog root (default: .)')
@click.option('--cli-author', help='author uid for cli user')
@click.pass_context
@_tmp_init_command()
def main_command(ctx, exec_path, cli_author):
    ctx.obj['exec-path'] = exec_path
    SESSION.initialize(exec_path)

    try:
        if cli_author is None:
            author = load_author_by_uid(getpass.getuser())
        else:
            author = load_author_by_uid(cli_author)
    except (OSError, ValueError):
        author = None

    if cli_author is not None and author is None:
        raise click.BadParameter('author not found', param_hint='--cli-author')

    ctx.obj['cli-author'] = author


def _session_result_func(result):
    if result:
        click.secho('Success!', fg='green')
    else:
        click.secho('Failure', fg='red')


class command_with_commit(object):
    def __init__(self, **options):
        self._options = options
        self._options.setdefault('result_func', _session_result_func)

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            with scoped_session_rw(session=SESSION, **self._options):
                return func(*args, **kwargs)
        return wrapper


class command_with_cli_author(object):
    def __init__(self):
        pass

    def __call__(self, func):
        def wrapper(*args, **kwargs):
            ctx = click.get_current_context()
            if ctx.obj['cli-author'] is None:
                raise click.BadParameter(
                    'mandatory cli author not defined',
                    param_hint='--cli-author',
                )
            return func(*args, **kwargs)
        return wrapper
