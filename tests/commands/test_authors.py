import pytest

from lpbm.lib.deprecated_command import DEPRECATED_MESSAGE


@pytest.mark.parametrize('commands', [
    ['--new'],
    ['--list'],
    ['--edit', '--id', '0'],
])
def test_commands_are_deprecated(command_caller, commands):
    with pytest.raises(SystemExit) as exc:
        command_caller(['authors'] + commands)
    assert str(exc.value) == DEPRECATED_MESSAGE
