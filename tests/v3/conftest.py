import shlex
import traceback

import pytest
import click.testing

from lpbm.v3.main import LPBMRootCommand


_CMD = LPBMRootCommand('lpbm-test')


class LPBMClient(object):
    def __init__(self, runner):
        self._runner = runner

    def run(self, cmd, inp=None):
        result = self._runner.invoke(_CMD, args=shlex.split(cmd), input=inp)
        if result.exit_code == -1:
            lines = ['Exception while calling command:\n']
            lines.extend(traceback.format_exception(*result.exc_info))
            assert False, ''.join(lines).strip()
        return result


@pytest.yield_fixture
def lpbm_client():
    runner = click.testing.CliRunner()
    with runner.isolated_filesystem():
        yield LPBMClient(runner)
