#!/usr/bin/env python

from distutils.core import setup

setup(
    name = "pykeg",
    version = "1.9.0",
    description = "Kegbot keg controller software",
    author = "mike wakerly",
    author_email = "mike@kegbot.org",
    url = "http://kegbot.org/",
    packages = [
      'pykeg',
      'pykeg.core',
      'pykeg.templates',
    ],
    package_dir = {
      'pykeg': '',
    },
    package_data = {
      'pykeg' : ['settings.py'],
      'pykeg.templates' : ['*.html', '*/*.html'],
    },
    data_files = [
      ('/etc/pykeg', ['settings.py']),
    ],
    scripts = [
      'bin/kb_core',
      'bin/kb_webserver',
    ],
)
