import os

import click

import lpbm.v3.lib.path as lpath

from lpbm.v3.meta.version import __version__


@click.group()
@click.version_option(version=__version__)
@click.option('-P', '--exec-path', default='.',
              type=click.Path(exists=True, resolve_path=True),
              help='path to the blog root (default: %(default)s)')
@click.pass_context
def main_command(ctx, exec_path):
    ctx.obj['exec-path'] = exec_path
    lpath.initialize(ctx)
