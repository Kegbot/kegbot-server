from channels.routing import route
from pykeg.web.ws.consumers import ws_connect, ws_disconnect


channel_routing = [
    route('websocket.connect', ws_connect, path=r"^/api/(?P<api_endpoint>[a-zA-Z0-9_]+)/$"),
    route('websocket.disconnect', ws_disconnect, path=r"^/api/(?P<api_endpoint>[a-zA-Z0-9_]+)/$"),
]
