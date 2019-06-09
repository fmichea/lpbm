import pytest

from lpbm.lib.deprecated_command import DEPRECATED_MESSAGE


@pytest.mark.parametrize('commands', [
    [],
])
def test_commands_are_deprecated(command_caller, commands):
    with pytest.raises(SystemExit) as exc:
        command_caller(['render'] + commands)
    assert str(exc.value) == DEPRECATED_MESSAGE
