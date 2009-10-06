# Copyright 2009 Mike Wakerly <opensource@hoho.com>
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

"""Kegnet server implementation."""

from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn
import cgi
import httplib
import inspect
import logging
import simplejson
import traceback
import threading

from pykeg.core import event
from pykeg.core import kb_common
from pykeg.core import util
from pykeg.core.net import kegnet_message

from pykeg.external.gflags import gflags

FLAGS = gflags.FLAGS

gflags.DEFINE_string('kb_core_bind_addr', kb_common.KB_CORE_DEFAULT_ADDR,
    'Address that the kegnet server should bind to.')

KB_EVENT = kb_common.KB_EVENT

class KegnetServer(ThreadingMixIn, HTTPServer):
  def __init__(self, kb_env, bind_addr=None):
    if bind_addr is None:
      bind_addr = FLAGS.kb_core_bind_addr
    if isinstance(bind_addr, basestring):
      self._addr = util.str_to_addr(bind_addr)
    else:
      self._addr = addr
    self._kb_env = kb_env
    self._services = {}
    self._handlers = {}
    self._lock = threading.Lock()
    self._logger = logging.getLogger('kegnet-server')
    HTTPServer.__init__(self, self._addr, KegnetServerRequestHandler)

  def AddService(self, service_cls):
    if service_cls in self._services:
      return
    service_inst = service_cls(self, self._kb_env)
    self._services[service_cls] = service_inst
    self._UpdateHandlers()

  @util.synchronized
  def GetHandler(self, path):
    while path.startswith('/'):
      path = path[1:]
    return self._handlers.get(path)

  @util.synchronized
  def _UpdateHandlers(self):
    self._handlers = {}
    for service in self._services.itervalues():
      for name, method in inspect.getmembers(service, inspect.ismethod):
        if not hasattr(method, 'endpoint'):
          continue
        self._handlers[method.endpoint] = method


class RequestWrapper:
  def __init__(self, handler, kb_env):
    self.http = handler
    self.kb_env = kb_env


class KegnetServerRequestHandler(BaseHTTPRequestHandler):
  protocol_version = 'HTTP/1.1'

  def _ExtractParams(self):
    """Extract HTTP GET parameters from path."""
    self.params = {}
    self.callback = ''
    qpos = self.path.find('?')
    if qpos >= 0:
      self.params = cgi.parse_qs(self.path[qpos+1:], keep_blank_values=1)
      self.path = self.path[:qpos]
      if 'callback' in self.params:
        self.callback = self.params.get('callback')[0]
        del self.params['callback']

  def log_request(self, code='-', size='-'):
    client_addr = '%s:%i' % self.client_address
    msg = ' '.join(map(str, (code, client_addr, self.command, self.path)))
    self.server._logger.debug(msg)

  def do_GET(self):
    self._ExtractParams()
    handler = self.server.GetHandler(self.path)
    if handler is None:
      return self._DoResponse(code=httplib.NOT_FOUND)

    wrapper = RequestWrapper(self, self.server._kb_env)

    try:
      result = handler(wrapper)
      if result is not None:
        if isinstance(result, kegnet_message.Message):
          body = result.AsJson()
        else:
          body = simplejson.dumps(result)
        if self.callback:
          body = self.callback + '(' + body + ')'
      else:
        body = ''
      self._DoResponse(body)
    except Exception, e:
      msg = traceback.print_exc()
      self._DoResponse(msg, code=httplib.BAD_REQUEST)

  do_OPTIONS = do_GET

  def _DoResponse(self, body=None, code=httplib.OK, type="text/plain"):
    if code != httplib.OK and body is None:
      body = '%s %s' % (code, httplib.responses[code])
    self.send_response(code)
    self.send_header("Content-type", type)
    self.send_header("Content-length", len(body))
    self.end_headers()
    self.wfile.write(body)


def ApiEndpoint(endpoint):
  """Decorator that sets attributes of an endpoint."""
  def decorate(f):
    setattr(f, 'endpoint', endpoint)
    return f
  return decorate


class KegnetService(object):
  def __init__(self, server, kb_env):
    self._server = server
    self._kb_env = kb_env

  def _PublishEvent(self, event, payload=None):
    self._kb_env.GetEventHub().PublishEvent(event, payload)


class KegnetBaseService(KegnetService):
  """Base service that must be implemented by all Kegnet servers.

  All methods wrapped with the ApiEndpoint decorator represent RESTful endpoints
  of this service.  Multiple services may be instantiated together, so endpoint
  names should be unique.
  """

  @ApiEndpoint('status/ping')
  def HandleStatusPing(self, request):
    """Always returns a simple 'alive' reply when the server is running."""
    response = {'status': 'ok'}
    return response

  @ApiEndpoint('status/version')
  def HandleStatusVersion(self, request):
    """Return the API version."""
    response = {'version': 1}
    return response


class KegnetFlowService(KegnetService):
  """Service that handles flow related requests."""

  @ApiEndpoint('meter/update')
  def HandleFlowUpdate(self, request):
    """Updates the Kegbot core with a new flow meter reading."""
    msg = kegnet_message.MeterUpdateMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.FLOW_DEV_ACTIVITY, msg)

  @ApiEndpoint('flow/start')
  def HandleFlowStart(self, request):
    """Force-starts a flow on the requested tap."""
    msg = kegnet_message.FlowStartRequestMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.START_FLOW, msg)

  @ApiEndpoint('flow/stop')
  def HandleFlowStop(self, request):
    """Force-stops a flow on the requested tap."""
    msg = kegnet_message.FlowStopRequestMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.END_FLOW, msg)

  @ApiEndpoint('flow/status')
  def HandleFlowStatus(self, request):
    msg = kegnet_message.FlowStatusRequestMessage(initial=request.http.params)
    tap = msg.tap_name
    flow_mgr = self._kb_env.GetFlowManager()
    flow = flow_mgr.GetFlow(tap)
    if flow:
      ret = kegnet_message.FlowUpdateMessage.FromFlow(flow)
      return ret
    else:
      return {}

  @ApiEndpoint('thermo/update')
  def HandleThermoUpdate(self, request):
    """Updates the Kegbot core with a new sensor value."""
    msg = kegnet_message.ThermoUpdateMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.THERMO_UPDATE, msg)

  @ApiEndpoint('auth/useradd')
  def HandleAuthUserAdd(self, request):
    """Indicates a user was added to an auth device."""
    msg = kegnet_message.AuthUserAddMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.AUTH_USER_ADDED, msg)

  @ApiEndpoint('auth/userremove')
  def HandleAuthUserRemove(self, request):
    """Indicates a user was removed from an auth device."""
    msg = kegnet_message.AuthUserAddMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.AUTH_USER_REMOVED, msg)

  @ApiEndpoint('auth/tokenadd')
  def HandleAuthTokenAdd(self, request):
    """Indicates a token was added to an auth device."""
    msg = kegnet_message.AuthTokenAddMessage(initial=request.http.params)
    self._PublishEvent(KB_EVENT.AUTH_TOKEN_ADDED, msg)
