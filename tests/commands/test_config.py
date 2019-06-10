import pytest

from lpbm.lib.deprecated_command import DEPRECATED_MESSAGE


@pytest.mark.parametrize('commands', [
    ['--list'],
    ['--check'],
    ['--set', 'foo=1'],
    ['--unset', 'foo'],
])
def test_commands_are_deprecated(command_caller, commands):
    with pytest.raises(SystemExit) as exc:
        command_caller(['config'] + commands)
    assert str(exc.value) == DEPRECATED_MESSAGE
