#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

VERSION = '0.8.5'
SHORT_DESCRIPTION = 'Kegbot kegerator controller software'
LONG_DESCRIPTION = """This package contains Kegbot core controller and Django
frontend package.

Kegbot is a hardware and software system to record and monitor access to a beer
kegerator.  For more information and documentation, see http://kegbot.org/
"""

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
    install_requires = [
      'django >= 1.3',
      'django-autoslug',
      'django-bootstrap-form',
      'django-debug-toolbar',
      'django-imagekit >= 2.0',
      'django-registration',
      'django-sentry',
      'django_extensions',
      'django-storages',
      'boto',

      'facebook-sdk >= 0.3.0',
      'django-socialregistration >= 0.5.4',

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
      'raven',
      'requests',  # needed by oauth

      # Celery and dependencies
      'Celery',
      'django-celery',
      'django-kombu',

      'poster',  # needed by foursquare
      'foursquare',

      # Tornado
      'tornado',
      'rjdj.djangotornado',
    ],
    dependency_links = [
        'https://github.com/mLewisLogic/foursquare/tarball/master#egg=foursquare',
        'https://github.com/rem/python-protobuf/tarball/master#egg=protobuf-2.4.1',
        'https://github.com/tzangms/django-bootstrap-form/tarball/master#egg=django-bootstrap-form',
        'https://github.com/rjdj/django-tornado/tarball/master#egg=rjdj.djangotornado',
    ],
    include_package_data = True,
    entry_points = {
      'console_scripts': ['instance=django.core.management:execute_manager'],
    },

)
