import pytest

import lpbm.v3.commands.root as mod


@pytest.mark.parametrize('val,exp', [
    (True, 'Success!'),
    (False, 'Failure'),
])
def test_session_result_func_shows_message_depending_on_param(monkeypatch, val, exp):
    msgs = []

    def func(msg, **kw):
        msgs.append(msg)

    monkeypatch.setattr(mod.click, 'secho', func)

    mod._session_result_func(val)
    assert msgs == [exp]
