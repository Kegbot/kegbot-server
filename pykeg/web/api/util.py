"""Utilities for processing API views."""

import logging
import sys
import traceback
import types

from addict import Dict
from django.conf import settings
from django.db.models.query import QuerySet
from django.http import Http404, HttpResponse
from google.protobuf.message import Message

from pykeg.core import models
from pykeg.proto import kbapi, protolib, protoutil
from pykeg.util import kbjson

from . import validate_jsonp

LOGGER = logging.getLogger(__name__)

ATTR_NEED_AUTH = "api_auth_required"


def is_api_request(request):
    return request.path.startswith("/api")


def needs_auth(viewfunc):
    return getattr(viewfunc, ATTR_NEED_AUTH, False)


def set_needs_auth(viewfunc):
    setattr(viewfunc, ATTR_NEED_AUTH, True)


def check_api_key(request):
    """Check a request for an API key."""
    keystr = request.META.get("HTTP_X_KEGBOT_API_KEY")
    if not keystr:
        keystr = request.POST.get("api_key", request.GET.get("api_key", None))
    if not keystr:
        raise kbapi.NoAuthTokenError('The parameter "api_key" is required')

    shared_key = settings.KEGBOT["KEGBOT_INSECURE_SHARED_API_KEY"]
    if shared_key and keystr == shared_key:
        return

    try:
        api_key = models.ApiKey.objects.get(key=keystr)
    except models.ApiKey.DoesNotExist:
        raise kbapi.BadApiKeyError("API key does not exist")

    if not api_key.is_active():
        raise kbapi.BadApiKeyError("Key and/or user is inactive")

    # TODO: remove me.
    if api_key.user and (not api_key.user.is_staff and not api_key.user.is_superuser):
        raise kbapi.PermissionDeniedError("User is not staff/superuser")


def to_json_error(e, exc_info):
    """Converts an exception to an API error response."""
    # Wrap some common exception types into kbapi types
    if isinstance(e, Http404):
        e = kbapi.NotFoundError(str(e))
    elif isinstance(e, ValueError):
        e = kbapi.BadRequestError(str(e))

    # Now determine the response based on the exception type.
    if isinstance(e, kbapi.Error):
        code = e.__class__.__name__
        http_code = e.HTTP_CODE
        message = e.Message()
    else:
        code = "ServerError"
        http_code = 500
        message = "An internal error occurred: %s" % str(e)
    result = {"error": {"code": code, "message": message}}
    if settings.DEBUG:
        result["error"]["traceback"] = "".join(traceback.format_exception(*exc_info))
    return result, http_code


def build_response(request, result_data, response_code=200):
    """Builds an HTTP response for JSON data."""
    callback = request.GET.get("callback")
    format = request.GET.get("format", None)
    debug = request.GET.get("debug", False)
    indent = 2

    json_str = kbjson.dumps(result_data, indent=indent)
    if callback and validate_jsonp.is_valid_jsonp_callback_value(callback):
        json_str = "%s(%s);" % (callback, json_str)

    if format == "html" or (settings.DEBUG and debug):
        html = "<html><body><pre>%s</pre></body></html>" % json_str
        return HttpResponse(html, content_type="text/html", status=response_code)
    else:
        return HttpResponse(json_str, content_type="application/json", status=response_code)


def prepare_data(data, inner=False):
    if isinstance(data, QuerySet) or isinstance(data, list):
        result = [prepare_data(d, True) for d in data]
        container = "objects"
    elif isinstance(data, dict):
        result = data
        container = "object"
    else:
        result = to_dict(data)
        container = "object"

    if inner:
        return result
    else:
        return {container: result}


def to_dict(data):
    if not isinstance(data, Message):
        data = protolib.ToProto(data, full=True)
    return Dict(protoutil.ProtoMessageToDict(data))


def wrap_exception(request, exception):
    """Returns a HttpResponse with the exception in JSON form."""
    exc_info = sys.exc_info()

    LOGGER.error(
        "%s: %s" % (exception.__class__.__name__, exception),
        exc_info=exc_info,
        extra={
            "status_code": 500,
            "request": request,
        },
    )

    # Don't wrap the exception during debugging.
    if settings.DEBUG and "deb" in request.GET:
        return None

    result_data, http_code = to_json_error(exception, exc_info)
    result_data["meta"] = {"result": "error"}
    return build_response(request, result_data, response_code=http_code)
