"""Celery tasks for Webhook plugin."""

import requests

from pykeg.celery import app
from pykeg.core.util import get_version
from pykeg.plugin import util
from pykeg.util import kbjson

logger = util.get_logger(__name__)


@app.task(name="webhook_post", expires=180)
def webhook_post(url, event_dict):
    """Posts an event to the supplied URL.

    The request body is a JSON dictionary of:
      * type: webhook message type (currently always 'event')
      * event_dict: webhook data (the event payload)

    Event payloads are in the same format as the /api/events/ endpoint.
    """
    logger.info("Posting webhook: url=%s event=%s" % (url, event_dict))

    hook_dict = {
        "type": "event",
        "data": event_dict,
    }

    headers = {
        "content-type": "application/json",
        "user-agent": "Kegbot/%s" % get_version(),
    }

    try:
        return requests.post(url, data=kbjson.dumps(hook_dict), headers=headers)
    except requests.exceptions.RequestException as e:
        logger.warning("Error posting hook: %s" % e)
        return False
