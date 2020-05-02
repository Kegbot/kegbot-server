from pykeg.celery import app


@app.task(name="core_checkin_task", bind=True, default_retry_delay=60 * 60 * 1, max_retries=3)
def core_checkin_task(self):
    from pykeg.core import checkin

    try:
        checkin.checkin()
    except checkin.CheckinError as exc:
        self.retry(exc=exc)
