import os

import click.testing

import lpbm.v3.main as mod


def test_main__lpbm_debug_set_must_be_parseable(lpbm_client, monkeypatch):
    monkeypatch.setitem(os.environ, 'LPBM_DEBUG', 'wdewed')

    result = lpbm_client.run('--version')
    assert result.exit_code == 1
    assert result.output == 'Invalid debug mode (LPBM_DEBUG) value: requires integer.\n'


def _test_exception_main(*a, **kw):
    raise Exception('test exceptions')


def test_main__lpbm_debug_on_with_no_debug(lpbm_client, monkeypatch):
    monkeypatch.setattr(mod.main_command, 'main', _test_exception_main)

    result = lpbm_client.run('--version', catch_exception=False)
    assert result.exit_code == -1


def test_main__lpbm_debug_on_exception_triggers_post_mortem(lpbm_client, monkeypatch):
    monkeypatch.setattr(mod.main_command, 'main', _test_exception_main)
    monkeypatch.setitem(os.environ, 'LPBM_DEBUG', '1')
    monkeypatch.setattr(mod.pdb, 'post_mortem', lambda x: x)

    result = lpbm_client.run('--version', catch_exception=False)
    assert result.exit_code == 1
