# Kegbot local settings, for travis-ci.org build

import os

HOME = os.environ['HOME']

DEBUG = True
TEMPLATE_DEBUG = DEBUG

DATABASES = {'default': {'ENGINE': 'django.db.backends.mysql', 'NAME': 'kegbot_travis_test', 'HOST': '', 'USER': 'root', 'PASSWORD': '', 'OPTIONS': {'init_command': 'SET storage_engine=INNODB'}}}

KEGBOT_ROOT = HOME + '/kegbot-data'

MEDIA_ROOT = KEGBOT_ROOT  + '/media'

STATIC_ROOT = KEGBOT_ROOT + '/static'

SECRET_KEY = 'testkey'

EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
EMAIL_FROM_ADDRESS = 'no-reply@example.com'
