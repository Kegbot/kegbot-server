from channels import Group
from kegbot.util import kbjson

from pykeg.proto import protolib

def publish_events(events):
    """Publishes a set of events on the websocket group."""
    events = [{'type': 'event', 'data': protolib.ToDict(e, True)} for e in events]
    for event in events:
        Group('api-events').send({
          "text": kbjson.dumps(event, indent=2),
        })
