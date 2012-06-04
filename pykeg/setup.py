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

VERSION = '0.9.0'
SHORT_DESCRIPTION = DOCLINES[0]
LONG_DESCRIPTION = '\n'.join(DOCLINES[2:])
REQUIRED = [
  'django >= 1.3',
  'django-autoslug',
  'django-bootstrap-form',
  'django-imagekit >= 2.0',
  'django-registration',
  'django-socialregistration >= 0.5.4',
  'django_extensions',

  'facebook-sdk >= 0.3.0',

  'MySQL-python',
  'pil',
  'protobuf >= 2.4.1',
  'pylcdui >= 0.5.5',
  'pysqlite>=2.0.3',
  'python-gflags >= 1.8',
  'South >= 0.7.3',
  'Sphinx',
  'django_nose',
  'tweepy',
  'django-icanhaz',
  'pytz',

  'requests', # needed by oauth
  'poster', # needed by foursquare
  'foursquare',
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

  ### Tornado
  'tornado',
  'rjdj.djangotornado',

  ### Raven
  'raven',

  ### Sentry
  'sentry',
  'django-sentry',
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
        'src/pykeg/bin/kegboard_daemon.py',
        'src/pykeg/bin/kegboard_monitor.py',
        'src/pykeg/bin/kegboard-tester.py',
        'src/pykeg/bin/kegbot-admin.py',
        'src/pykeg/bin/kegbot_core.py',
        'src/pykeg/bin/kegbot_master.py',
        'src/pykeg/bin/lcd_daemon.py',
        'src/pykeg/bin/rfid_daemon.py',
        'src/pykeg/bin/sound_server.py',
      ],
      install_requires = DEPENDENCIES,
      dependency_links = [
          'https://github.com/rem/python-protobuf/tarball/master#egg=protobuf-2.4.1',
          'https://github.com/tzangms/django-bootstrap-form/tarball/master#egg=django-bootstrap-form',
          'https://github.com/rjdj/django-tornado/tarball/master#egg=rjdj.djangotornado',
      ],
      include_package_data = True,
      entry_points = {
        'console_scripts': ['instance=django.core.management:execute_manager'],
      },

  )

if __name__ == '__main__':
  setup_package()
