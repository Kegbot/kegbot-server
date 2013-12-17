### Constants

# Package version.
__version__ = '0.9.14'

# Internal version number, bumped every time "kb_upgrade" is needed.
EPOCH = 103

### Celery setup
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .celery import app as celery_app