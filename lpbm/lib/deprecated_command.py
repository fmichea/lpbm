import sys

DEPRECATED_MESSAGE = (
    'ERROR: Deprecated, please migrate to jekyll using the migrate command or\n' +
    '  downgrade to the previous version.'
)


def deprecated_command():
    sys.exit(DEPRECATED_MESSAGE)
