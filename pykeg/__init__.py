### Constants

# Internal version number, bumped every time "kegbot upgrade" is needed.
EPOCH = 105

try:
    import local_settings
    IS_SETUP = True
except ImportError:
    IS_SETUP = False

### Celery setup
# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
# HACK: Avoid bootstrapping Celery until setup has been run,
# since it depends on settings -> local_settings.
if IS_SETUP:
    from .celery import app as celery_app