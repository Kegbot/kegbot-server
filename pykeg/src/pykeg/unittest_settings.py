from settings import *

DEBUG = True
TEMPLATE_DEBUG = DEBUG
ADMINS = ()
MANAGERS = ADMINS
DATABASE_ENGINE = 'sqlite3'
DATABASE_NAME = 'unittest_db.sqlite.bin'
TIME_ZONE = 'America/Los_Angeles'
LANGUAGE_CODE = 'en-us'
SITE_ID = 1
MEDIA_ROOT = ''
MEDIA_URL = ''
ADMIN_MEDIA_PREFIX = '/media/'
SECRET_KEY = ''

# add external paths
import os
import sys
_local_dir = os.path.dirname(sys.modules[__name__].__file__)
_package_dir = os.path.normpath(os.path.join(_local_dir, '..'))
sys.path.insert(0, os.path.join(_package_dir, 'pykeg', 'external'))
