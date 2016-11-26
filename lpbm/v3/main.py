import os
import pdb
import sys
import traceback

import click

from lpbm.v3.commands import main_command


class LPBMRootCommand(click.BaseCommand):
    def main(self, *a, **kw):
        try:
            debug_mode = bool(int(os.environ.get('LPBM_DEBUG', 0)))
        except Exception as exc:
            click.echo('Invalid debug mode (LPBM_DEBUG) value: requires integer.')
            sys.exit(1)

        try:
            kw.update({'prog_name': 'lpbm', 'obj': dict()})
            main_command.main(*a, **kw)
        except Exception as exc:
            # If we have debugging mode enabled through the environment, then we
            # want to provide a pdb prompt on exception, otherwise we simply raise
            # the exception again.
            if not debug_mode:
                raise
            traceback.print_exc()
            pdb.post_mortem(sys.exc_info()[2])
            sys.exit(1)


def main():
    return LPBMRootCommand('lpbm').main()
