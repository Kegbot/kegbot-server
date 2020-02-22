#!/usr/bin/env python

"""Kegbot Server package.

Kegbot is a hardware and software system to record and monitor access to a
kegerator.  For more information and documentation, see http://kegbot.org/
"""

from setuptools import setup, find_packages

VERSION = '1.2.3'
DOCLINES = __doc__.split('\n')

SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])

setup(
    name='kegbot',
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Bevbot LLC',
    author_email='info@bevbot.com',
    url='https://kegbot.org/',
    packages=find_packages(),
    scripts=[
        'bin/kegbot',
        'bin/setup-kegbot.py',
    ],
    dependency_links=[
        'https://github.com/rem/python-protobuf/tarball/master#egg=protobuf-2.4.1',
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['instance=django.core.management:execute_manager'],
    },
)
