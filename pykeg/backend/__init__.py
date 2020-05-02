from django.conf import settings
from django.utils.module_loading import import_string


def get_kegbot_backend():
    return import_string(settings.KEGBOT_BACKEND)()
