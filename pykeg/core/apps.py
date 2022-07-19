from django.apps import AppConfig


class CoreApp(AppConfig):
    name = "pykeg.core"

    def ready(self):
        # Implicitly connect signal handlers decorated with @receiver.
        from . import signal_handlers
