#!/usr/bin/env python

"""Kegbot Beer Kegerator Server package.

Kegbot is a hardware and software system to record and monitor access to a beer
kegerator.  For more information and documentation, see http://kegbot.org/
"""

from setuptools import setup, find_packages
from pykeg import __version__ as VERSION

DOCLINES = __doc__.split('\n')

SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])
DEPENDENCIES = [
  'kegbot-pyutils >= 0.1.4',
  'kegbot-api >= 0.1.6',

  'django >= 1.3',
  'django-autoslug',
  'django-imagekit >= 2.0',
  'django-registration',
  'django-socialregistration >= 0.5.4',
  'django_extensions',

  'Celery',
  'django-celery',
  'django-kombu',

  'South >= 0.7.3',
  'django-crispy-forms',
  'django-icanhaz',
  'django_nose',
  'facebook-sdk >= 0.3.0',
  'foursquare',
  'gunicorn >= 0.16.1',
  'poster', # needed by foursquare
  'pylcdui >= 0.5.5',
  'protobuf >= 2.4.1',
  'python-gflags >= 1.8',
  'pytz',
  'requests', # needed by oauth
  'tweepy',
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
        'bin/kegbot-admin.py',
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
