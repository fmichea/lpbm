import shlex
import shutil
import tempfile
import traceback

import pytest
import click.testing

from lpbm.v3.lib.model import SESSION
from lpbm.v3.main import LPBMRootCommand


@pytest.yield_fixture(autouse=True, scope='function')
def test_session_reset():
    try:
        yield
    finally:
        SESSION.rollback()


@pytest.yield_fixture(autouse=True, scope='session')
def testsuite_tempdir():
    root = tempfile.mkdtemp(prefix='tmp-lpbm-testsuite-')
    try:
        yield root
    finally:
        shutil.rmtree(root)


@pytest.yield_fixture()
def test_tempdir(testsuite_tempdir):
    root = tempfile.mkdtemp(prefix='tmp-test-', dir=testsuite_tempdir)
    try:
        yield root
    finally:
        shutil.rmtree(root)


@pytest.yield_fixture(autouse=True, scope='function')
def model_name_to_class_mapping_reset(monkeypatch):
    import lpbm.v3.lib.model.data as mod
    monkeypatch.setattr(mod, 'MODEL_NAME_TO_CLASS', dict())
    yield


_CMD = LPBMRootCommand('lpbm-test')


class LPBMClient(object):
    def __init__(self, runner):
        self._runner = runner

    def run(self, cmd, inp=None, exit_code=None):
        result = self._runner.invoke(
            _CMD, args=shlex.split(cmd), input=inp, catch_exceptions=False)
        if exit_code is not None:
            output = 'Exit code was {0} (expected {1}); output:\n{2}'
            output = output.format(result.exit_code, exit_code, result.output)
            assert result.exit_code == exit_code, output
        return result


@pytest.yield_fixture
def lpbm_client():
    runner = click.testing.CliRunner()
    with runner.isolated_filesystem():
        yield LPBMClient(runner)
