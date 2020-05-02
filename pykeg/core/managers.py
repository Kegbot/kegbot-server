from django.db import models
from pykeg.core import kb_common


class SessionManager(models.Manager):
    """Manager for session models."""

    def valid(self):
        return self.filter(volume_ml__gt=kb_common.MIN_SESSION_VOLUME_DISPLAY_ML)


class SystemEventManager(models.Manager):
    def timeline(self):
        return self.filter(kind__in=("drink_poured", "session_joined", "keg_tapped", "keg_ended"))

    def short_timeline(self):
        """Limited to 20 events."""
        return self.timeline()[:20]
