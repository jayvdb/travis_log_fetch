# -*- coding: utf-8 -*-
"""Setup module."""
from __future__ import absolute_import
from __future__ import unicode_literals

import os
import sys

from setuptools import find_packages
from setuptools import setup

from setuptools.command.test import test as TestCommand  # noqa: N812

PY26 = sys.version_info[0:2] < (2, 7)


class PyTest(TestCommand):
    """Test harness."""

    user_options = []

    def initialize_options(self):
        """Initialise options hook."""
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        """Finalize options hook."""
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        """Run tests hook."""
        import pytest  # noqa: delayed import
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


_user = 'jayvdb'
_package_name = 'travis_log_fetch'

dependencies = [
    'travispy',
    'github3.py>=1.0.0a1',
    'parse',
    'python-dateutil',
]
dependencies.append('ConfigArgParse>=0.10.0' if PY26 else 'ConfigArgParse')

dependency_links = [
    'git+https://github.com/jayvdb/travispy@fetch-log#egg=travispy-0.3.3'
]

_package_init_py = os.path.join(os.path.dirname(__file__),
                                _package_name,
                                '__init__.py')

with open(_package_init_py) as version_file:
    version_line = [line for line in version_file.readlines()
                    if line.startswith('__version__')][0]

version = version_line.split(' = ')[1][1:-2]

with open('README-pypi.rst') as readme_file:
    long_description = readme_file.read()

slug = _user + '/' + _package_name

setup(
    name=_package_name,
    packages=find_packages(),
    version=version,
    install_requires=dependencies,
    dependency_links=dependency_links,
    entry_points={
        'console_scripts': [
            'travis_log_fetch = travis_log_fetch:main',
        ],
    },
    description='Command line tool to fetch Travis-CI logs.',
    long_description=long_description,
    author='John Vandenberg',
    author_email='jayvdb@gmail.com',
    license='MIT',
    url='https://github.com/' + slug,
    download_url='https://github.com/' + slug + '/tarball/' + version,
    keywords=['travis', 'travis-ci', 'travispy'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Unix',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Quality Assurance',
        'Topic :: Software Development :: Testing',
        'Topic :: Utilities'],
    # tests
    tests_require=['pytest'],
    cmdclass={'test': PyTest},
)
