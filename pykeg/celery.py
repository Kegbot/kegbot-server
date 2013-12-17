from __future__ import absolute_import

import os
from celery import Celery
from django.conf import settings

# set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pykeg.settings')

app = Celery('pykeg')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

plugin_tasks = lambda: ['.'.join(x.split('.')[:-2]) for x in settings.KEGBOT_PLUGINS]
app.autodiscover_tasks(plugin_tasks())
