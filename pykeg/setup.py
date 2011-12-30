#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

VERSION = "0.8.4"
SHORT_DESCRIPTION = "Kegbot kegerator controller software"
LONG_DESCRIPTION = """This package contains Kegbot core controller and Django
frontend package.

Kegbot is a hardware and software system to record and monitor access to a beer
kegerator.  For more information and documentation, see http://kegbot.org/
"""

setup(
    name = "kegbot",
    version = VERSION,
    description = SHORT_DESCRIPTION,
    long_description = LONG_DESCRIPTION,
    author = "mike wakerly",
    author_email = "opensource@hoho.com",
    url = "http://kegbot.org/",
    packages = find_packages('src'),
    package_dir = {
      '' : 'src',
    },
    scripts = [
      'distribute_setup.py',
      'src/pykeg/bin/fb_publisher.py',
      'src/pykeg/bin/kegboard_daemon.py',
      'src/pykeg/bin/kegboard_monitor.py',
      'src/pykeg/bin/kegboard-tester.py',
      'src/pykeg/bin/kegbot-admin.py',
      'src/pykeg/bin/kegbot_core.py',
      'src/pykeg/bin/kegbot_master.py',
      'src/pykeg/bin/kegbot_twitter.py',
      'src/pykeg/bin/kegnetproxy.py',
      'src/pykeg/bin/lcd_daemon.py',
      'src/pykeg/bin/rfid_daemon.py',
      'src/pykeg/bin/sound_server.py',
    ],
    install_requires = [
      'django >= 1.3',
      'django-autoslug',
      'django-bootstrap-form',
      'django-debug-toolbar',
      'django-imagekit >= 1.0',
      'django-registration',
      'django-sentry',
      'django_extensions',
      'django-storages',
      'boto',

      # NOTE(mikey): socialregistration does not yet declare the
      # facebook-python-sdk prerequisite for itself.
      'facebook-python-sdk',
      'django-socialregistration >= 0.4.2',

      #'MySQL-python',
      #'pil',
      'protobuf >= 2.4.1',
      'pylcdui >= 0.5.5',
      #'pysqlite>=2.0.3',
      'python-gflags >= 1.3',
      'South >= 0.7.3',
      'Sphinx',
      'django_nose',
      #'python-openid >= 2.2.5',  # removeme once PIL package works
      'tweepy',
      'pytz',
      'raven',

      # Celery and dependencies
      'Celery',
      'django-celery',
      'django-kombu',
    ],
    dependency_links = [
        'https://github.com/rem/python-protobuf/tarball/master#egg=protobuf-2.4.1',
        'http://dist.repoze.org/PIL-1.1.6.tar.gz',
        'http://kegbot.org/kmedia/python-openid-2.2.5.tgz',
        'https://github.com/tzangms/django-bootstrap-form/tarball/master#egg=django-bootstrap-form',

        # Self-maintained package due to upstream issue:
        # http://github.com/facebook/python-sdk/issues/#issue/21
        'http://github.com/downloads/mik3y/python-sdk/facebook-python-sdk-0.1-1.tar.gz',
    ],
    include_package_data = True,

)
