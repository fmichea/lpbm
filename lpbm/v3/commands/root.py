import click

from lpbm.v3.lib.model import SESSION, scoped_session_rw
from lpbm.v3.meta.version import __version__


@click.group()
@click.version_option(version=__version__)
@click.option('-P', '--exec-path', default='.',
              type=click.Path(exists=True, resolve_path=True),
              help='path to the blog root (default: %(default)s)')
@click.pass_context
def main_command(ctx, exec_path):
    ctx.obj['exec-path'] = exec_path
    SESSION.initialize(exec_path)


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
