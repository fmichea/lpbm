import os
import shlex
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

_ROOT = os.path.abspath(os.path.dirname(__file__))


class PyTest(TestCommand):
    user_options = [
        ('args=', 'a', 'Additional arguments to pass to py.test'),
        ('debug=', 'D', 'Enable debugging of test suite (on, first, off)'),
        ('coverage=', 'C', 'Enable coverage of the test project (on, keep-result, off)'),
        ('exec-only=', 'k', 'Filter tests by test name or filename'),
    ]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.args, self.debug, self.coverage, self.exec_only = [], 'off', 'on', ''

    def run(self):
        import pytest
        args = []
        if self.debug in ['first', 'on']:
            if self.debug == 'first':
                args.append('-x')
            args.extend(['--pdb', '-vv', '-s'])
        if self.coverage in ['on', 'keep-result']:
            args.extend([
                '--cov-config', os.path.join(_ROOT, '.coveragerc'),
                '--cov', 'lpbm',
                '--cov-report', 'term-missing',
                '--no-cov-on-fail',
            ])
        if self.exec_only:
            args.append('-k{}'.format(self.exec_only))
        if self.args:
            args.extend(shlex.split(self.args))
        args.append(os.path.join(_ROOT, 'tests'))
        print('execute: py.test', ' '.join(shlex.quote(arg) for arg in args))
        try:
            errno = pytest.main(args)
        finally:
            cov_file = os.path.join(_ROOT, '.coverage')
            if self.coverage != 'keep-result' and os.path.exists(cov_file):
                os.unlink(cov_file)
        sys.exit(errno)


setup(
    # General information.
    name='lpbm',
    description='Lightweight personal blog maker',
    url='http://github.com/fmichea/lpbm',

    # Version information.
    license='BSD',
    version='2.0.0',

    # Author.
    author='Franck Michea',
    author_email='franck.michea@gmail.com',

    # File information.
    install_requires=open('requirements/command.txt').readlines(),
    packages=find_packages(exclude=['test', 'doc']),
    package_data={'': ['*.css', '*.html']},
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'lpbm = lpbm.main:main',
        ],
    },
    cmdclass={
        'test': PyTest,
    },

    # Categories
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
