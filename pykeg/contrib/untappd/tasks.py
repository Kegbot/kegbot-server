"""Celery tasks for Untappd."""

from builtins import str
import requests

import foursquare

from pykeg.celery import app
from pykeg.plugin import util

logger = util.get_logger(__name__)


@app.task(name="untappd_checkin", expires=60)
def untappd_checkin(
    token,
    beer_id,
    timezone_name,
    shout=None,
    foursquare_client_id=None,
    foursquare_client_secret=None,
    foursquare_venue_id=None,
):
    logger.info(
        "Checking in: token=%s beer_id=%s timezone_name=%s" % (token, beer_id, timezone_name)
    )

    # Untappd *requires* lat/lng information when checking in with a
    # Foursquare id.  A bit silly since here we go fetching it just
    # to pass this "security" check..
    geolat = geolng = None
    if foursquare_venue_id:
        fs = foursquare.Foursquare(
            client_id=foursquare_client_id, client_secret=foursquare_client_secret
        )
        logger.info("Fetching venue location info from Foursquare")
        try:
            venue_info = fs.venues(foursquare_venue_id).get("venue", {})
            geolat = venue_info.get("location", {}).get("lat")
            geolng = venue_info.get("location", {}).get("lng")
            logger.info("Resolved lat/lng: {}, {}".format(geolat, geolng))
        except foursquare.FoursquareException as e:
            logger.error("Error fetching Foursquare information: {}".format(e))

    # TODO(mikey): API does not appear to support Olso tz names for
    # the timezone parameter.  Report as GMT, as it doesn't seem to
    # be meaningful.
    data = {
        "bid": beer_id,
        "gmt_offset": 0,
        "timezone": "GMT",
    }

    if foursquare_venue_id and geolat and geolng:
        logger.info("Attaching Foursquare venue {}".format(foursquare_venue_id))
        data["foursquare_id"] = foursquare_venue_id
        data["geolat"] = geolat
        data["geolng"] = geolng

    if shout:
        data["shout"] = shout

    params = {"access_token": token}
    url = "https://api.untappd.com/v4/checkin/add"
    r = requests.post(url, params=params, data=data)
    logger.info("Response: %s" % str(r.text))
