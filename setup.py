#!/usr/bin/env python

"""Kegbot Server package.

Kegbot is a hardware and software system to record and monitor access to a
kegerator.  For more information and documentation, see http://kegbot.org/
"""

from setuptools import setup, find_packages

VERSION = '1.0.2'
DOCLINES = __doc__.split('\n')

SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])
DEPENDENCIES = [
  'kegbot-pyutils == 0.1.7',
  'kegbot-api == 0.1.16',

  'Django == 1.6.5',
  'django-imagekit == 3.1',
  'django-registration == 1.0',
  'django-socialregistration == 0.5.10',
  'django-bootstrap-pagination == 0.1.10',

  'Celery == 3.1.11',
  'kombu == 3.0.16',

  'South == 0.8.4',
  'django-crispy-forms == 1.2.8',
  'foursquare == 2014.04.10',
  'gunicorn == 18.0',
  'MySQL-python == 1.2.5',
  'pillow == 2.4.0',
  'protobuf == 2.5.0',
  'python-gflags == 2.0',
  'django-redis == 3.6.1',
  'pytz == 2014.2',
  'redis == 2.9.1',
  'requests == 2.2.1',
  'tweepy == 2.2',
  'jsonfield == 0.9.20',
]

def setup_package():
  setup(
      name = 'kegbot',
      version = VERSION,
      description = SHORT_DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      author = 'Bevbot LLC',
      author_email = 'info@bevbot.com',
      url = 'https://kegbot.org/',
      packages = find_packages(),
      scripts = [
        'bin/kegbot',
        'bin/setup-kegbot.py',
      ],
      install_requires = DEPENDENCIES,
      dependency_links = [
          'https://github.com/rem/python-protobuf/tarball/master#egg=protobuf-2.4.1',
      ],
      include_package_data = True,
      entry_points = {
        'console_scripts': ['instance=django.core.management:execute_manager'],
      },
  )

if __name__ == '__main__':
  setup_package()
