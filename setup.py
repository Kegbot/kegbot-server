#!/usr/bin/env python

"""Kegbot Server package.

Kegbot is a hardware and software system to record and monitor access to a
kegerator.  For more information and documentation, see http://kegbot.org/
"""

from setuptools import setup

VERSION = '1.3.0b1'
DOCLINES = __doc__.split('\n')

SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])

setup(
    name='kegbot',
    version=VERSION,
    description=SHORT_DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    author='Kegbot Project',
    author_email='info@kegbot.org',
    url='https://kegbot.org/',
    scripts=[
        'bin/kegbot',
    ],
)
