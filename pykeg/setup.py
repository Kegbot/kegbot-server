#!/usr/bin/env python

from distribute_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

VERSION = "0.7.7"
SHORT_DESCRIPTION = "Kegbot kegerator controller software"
LONG_DESCRIPTION = """This package contains Kegbot core controller and Django
frontend package.

Kegbot is a hardware and software system to record and monitor access to a beer
kegerator.  For more information and documentation, see http://kegbot.org/

**Note:** This package is still *experimental* and subject to change.
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
      'src/pykeg/bin/kegbot-admin.py',
      'src/pykeg/bin/kegbot_core.py',
      'src/pykeg/bin/kegbot_master.py',
      'src/pykeg/bin/kegbot_twitter.py',
      'src/pykeg/bin/lcd_daemon.py',
      'src/pykeg/bin/rfid_daemon.py',
      'src/pykeg/bin/sound_server.py',
    ],
    install_requires = [
      'django >= 1.2',
      'django-autoslug',
      'django-imagekit >= 0.3.3',
      'django-registration',
      'django_extensions',

      # NOTE(mikey): socialregistration does not yet declare the
      # facebook-python-sdk prerequisite for itself.
      'facebook-python-sdk',
      'django-socialregistration >= 0.4.2',

      #'MySQL-python',
      #'pil',
      'pylcdui >= 0.5.5',
      #'pysqlite>=2.0.3',
      'python-gflags >= 1.3',
      'South >= 0.7',
      'Sphinx',
      'django_nose',
      #'python-openid >= 2.2.5',  # removeme once PIL package works
      'tweepy',
      'pytz',
    ],
    dependency_links = [
        'http://dist.repoze.org/PIL-1.1.6.tar.gz',
        'http://kegbot.org/kmedia/python-openid-2.2.5.tgz',

        # Self-maintained package due to upstream issue:
        # http://github.com/facebook/python-sdk/issues/#issue/21
        'http://github.com/downloads/mik3y/python-sdk/facebook-python-sdk-0.1-1.tar.gz',
    ],
    include_package_data = True,

)
