#!/usr/bin/env python

"""Kegbot Beer Kegerator Server package.

Kegbot is a hardware and software system to record and monitor access to a beer
kegerator.  For more information and documentation, see http://kegbot.org/
"""

from setuptools import setup, find_packages

VERSION = '0.9.16'
DOCLINES = __doc__.split('\n')

SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])
DEPENDENCIES = [
  'kegbot-pyutils == 0.1.7',
  'kegbot-api == 0.1.8',

  'Django == 1.6.1',
  'django-imagekit == 3.1',
  'django-registration == 1.0',
  'django-socialregistration == 0.5.10',
  'django-bootstrap-pagination == 0.1.10',

  'django-celery == 3.1.1',
  'Celery == 3.1.6',

  'South == 0.8.1',
  'django-crispy-forms == 1.2.8',
  'django-icanhaz == 0.2.1',
  'django_nose == 1.2',
  'foursquare == 20130402',
  'gunicorn == 18.0',
  'MySQL-python == 1.2.4',
  'pillow == 2.1.0',
  'protobuf == 2.5.0',
  'python-gflags == 2.0',
  'python-memcached == 1.51',
  'pytz == 2013b',
  'requests == 2.0.1',
  'tweepy == 2.0',
  'mock == 1.0.1',
]

def setup_package():
  setup(
      name = 'kegbot',
      version = VERSION,
      description = SHORT_DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      author = 'mike wakerly',
      author_email = 'opensource@hoho.com',
      url = 'http://kegbot.org/',
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
