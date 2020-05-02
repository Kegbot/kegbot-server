"""Celery tasks for Foursquare."""

import os
import foursquare
import datetime
import PIL

from io import StringIO
from pykeg.celery import app
from pykeg.plugin import util
from pykeg.core.util import download_to_tempfile

MAX_CHECKIN_AGE = datetime.timedelta(minutes=30)

logger = util.get_logger(__name__)


@app.task(name="foursquare_checkin", expires=60)
def foursquare_checkin(token, venue_id, image_url=None):
    client = foursquare.Foursquare(access_token=token)
    logger.info("Checkin request: token=%s venue=%s" % (token, venue_id))

    checkin = None
    last_checkin = _get_last_checkin(client)
    if last_checkin:
        venue = last_checkin.get("venue", {}).get("id", "")
        if venue == venue_id:
            when = datetime.datetime.fromtimestamp(int(last_checkin.get("createdAt", 0)))
            if (when + MAX_CHECKIN_AGE) > datetime.datetime.now():
                logger.info("Reusing last checkin.")
                checkin = last_checkin

    if not checkin:
        logger.info("Performing fresh checkin.")
        checkin = client.checkins.add(params={"venueId": venue_id}).get("checkin")

    checkin_id = checkin.get("id")

    image_path = None
    if image_url:
        logger.info("Has image, downloading: {}".format(image_url))
        try:
            image_path = download_to_tempfile(image_url)
        except IOError as e:
            logger.warning("Couldn't download file: {}".format(e))

    image_bytes = None
    if image_path:
        try:
            image_bytes = StringIO()
            im = PIL.Image.open(image_path)
            im.convert("RGB").save(image_bytes, "JPEG")
            image_bytes.seek(0)
        except IOError as e:
            logger.warning("Error reading image: {}".format(e))
        finally:
            os.unlink(image_path)

    if image_bytes:
        logger.info("Checkin complete, adding photo. Checkin id: {}".format(checkin_id))
        client.photos.add(params={"checkinId": checkin_id}, photo_data=image_bytes)

    return checkin_id


def _get_last_checkin(client):
    result = client.users.checkins(params={"limit": 1})
    items = result.get("checkins", {}).get("items", [])
    if items:
        return items[0]
    return None
