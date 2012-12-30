#!/usr/bin/env python
"""Kegbot kegerator controller software

This package contains Kegbot core controller and Django
frontend package.

Kegbot is a hardware and software system to record and monitor access to a beer
kegerator.  For more information and documentation, see http://kegbot.org/
"""

DOCLINES = __doc__.split('\n')

# Change this to True to include optional dependencies
USE_OPTIONAL = False

VERSION = '0.9.5'
SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])
REQUIRED = [
  'kegbot-pyutils >= 0.1.4',
  'kegbot-api >= 0.1.2',

  'django >= 1.3',
  'django-autoslug',
  'django-imagekit >= 2.0',
  'django-registration',
  'django-socialregistration >= 0.5.4',
  'django_extensions',

  'MySQL-python',
  'South >= 0.7.3',
  'django-crispy-forms',
  'django-icanhaz',
  'django_nose',
  'facebook-sdk >= 0.3.0',
  'foursquare',
  'gunicorn >= 0.16.1',
  'pillow',
  'poster', # needed by foursquare
  'protobuf >= 2.4.1',
  'pylcdui >= 0.5.5',
  'pysqlite>=2.0.3',
  'python-gflags >= 1.8',
  'pytz',
  'requests', # needed by oauth
  'tweepy',
]

OPTIONAL = [
  ### Optional modules.
  # This modules 'pip install'd manually.  If you add to this list, also
  # update pykeg.core.optional_modules with a new 'HAVE_<MODULE>' flag, as
  # well as pykeg.settings (if needed).

  ### django-debug-toolbar
  'django-debug-toolbar',

  ### Celery
  'Celery',
  'django-celery',
  'django-kombu',

  ### Raven
  'raven',

  ### Sentry
  'sentry',
]

DEPENDENCIES = REQUIRED
if USE_OPTIONAL:
  DEPENDENCIES += OPTIONAL


def setup_package():
  from distribute_setup import use_setuptools
  use_setuptools()
  from setuptools import setup, find_packages

  setup(
      name = 'kegbot',
      version = VERSION,
      description = SHORT_DESCRIPTION,
      long_description = LONG_DESCRIPTION,
      author = 'mike wakerly',
      author_email = 'opensource@hoho.com',
      url = 'http://kegbot.org/',
      packages = find_packages('src'),
      package_dir = {
        '' : 'src',
      },
      scripts = [
        'distribute_setup.py',
        'bin/kegbot-admin.py',
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
