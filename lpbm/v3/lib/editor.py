import os
import subprocess


def edit(filename):
    editor = os.environ.get('EDITOR', 'vim')
    subprocess.check_call([editor, filename])
