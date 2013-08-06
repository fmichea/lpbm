try:
    from setuptools import setup, find_packages
except ImportError:
    import distribute_setup
    distribute_setup.use_setuptools()
    from setuptools import setup, find_packages

setup(
    # General information.
    name='lpbm',
    description='Lightweight personal blog maker',
    url='http://bitbucket.org/kushou/lpbm',

    # Version information.
    license='BSD',
    version='2.0.0a3',

    # Author.
    author='Franck Michea',
    author_email='franck.michea@gmail.com',

    # File information.
    install_requires=open('requirements.txt').readlines(),
    packages=find_packages(exclude=['test', 'doc']),
    package_data={'': ['*.css', '*.html']},
    include_package_data=True,
    entry_points = {
        'console_scripts': [
            'lpbm = lpbm.main:main',
        ],
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
