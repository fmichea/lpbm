import os
import shutil
import tempfile

import pytest

from lpbm.main import main

_ROOT = os.path.abspath(os.path.dirname(__file__))


@pytest.yield_fixture
def test_tempdir():
    try:
        tmpdir = tempfile.mkdtemp(prefix='lpbm-test-')
        yield tmpdir
    finally:
        # shutil.rmtree(tmpdir)
        pass


@pytest.yield_fixture
def test_result_tempdir(test_tempdir):
    result_dir = os.path.join(test_tempdir, 'result-jekyll')
    os.mkdir(result_dir, 0o755)
    yield result_dir


@pytest.yield_fixture
def command_caller(test_result_tempdir):
    paths = set()

    def _link_path(root):
        return os.path.join(root, 'result-jekyll')

    def command(args, blog='test-blog-1'):
        root = os.path.join(_ROOT, 'data', blog)
        paths.add(root)

        os.symlink(test_result_tempdir, _link_path(root))
        args = ['--exec-path', root] + args
        return main(args=args)

    try:
        yield command
    finally:
        for root in paths:
            os.unlink(_link_path(root))
