"""Admin operations endpoints: dashboard, backups, logs, email test, bugreport.

These replace the corresponding kegadmin pages. Everything here is
admin-only.
"""

import datetime
import io
import logging
import os
import zipfile
from operator import itemgetter

import redis
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound
from rest_framework.response import Response

from pykeg.backup import backup as backup_lib
from pykeg.core import models, tasks
from pykeg.logging.handlers import RedisListHandler
from pykeg.util import bugreport as bugreport_util
from pykeg.util.email import build_message

from . import permissions, serializers

logger = logging.getLogger(__name__)


@extend_schema(responses=serializers.AdminDashboardSerializer)
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def dashboard(request):
    """System health summary for the admin dashboard."""
    site = getattr(request, "kbsite", None) or models.KegbotSite.get()

    redis_error = None
    try:
        client = redis.StrictRedis.from_url(settings.KEGBOT["REDIS_URL"])
        client.ping()
    except redis.RedisError as e:
        redis_error = str(e) or "Unknown error."

    guestless_users = models.User.objects.exclude(username="guest")
    recent_time = timezone.now() - datetime.timedelta(days=30)
    payload = {
        "email_configured": site.email_is_configured(),
        "redis_error": redis_error,
        "num_users": guestless_users.filter(is_active=True).count(),
        "num_new_users": guestless_users.filter(date_joined__gte=recent_time).count(),
    }
    return Response(serializers.AdminDashboardSerializer(instance=payload).data)


@extend_schema(request=None, responses=OpenApiTypes.OBJECT)
@api_view(["GET", "POST"])
@permission_classes([permissions.IsAdminUser])
def backups(request):
    """Lists existing backups (GET) or starts building a new one (POST)."""
    if request.method == "POST":
        tasks.build_backup.delay()
        return Response({"started": True}, status=status.HTTP_202_ACCEPTED)

    storage = default_storage
    results = []
    if storage.exists(backup_lib.BACKUPS_DIRNAME):
        _, files = storage.listdir(backup_lib.BACKUPS_DIRNAME)
        for filename in files:
            if not filename.endswith("zip"):
                continue
            storage_filename = os.path.join(backup_lib.BACKUPS_DIRNAME, filename)
            with storage.open(storage_filename, mode="rb") as backup_file:
                archive = zipfile.ZipFile(backup_file)
                metadata = backup_lib.read_metadata(archive)
                metadata["size_bytes"] = storage.size(storage_filename)
                metadata["url"] = storage.url(storage_filename)
                metadata["backup_name"] = filename
                results.append(metadata)
    results.sort(key=itemgetter(backup_lib.META_CREATED_TIME), reverse=True)
    return Response(results)


@extend_schema(request=None, responses=None)
@api_view(["DELETE"])
@permission_classes([permissions.IsAdminUser])
def delete_backup(request, filename):
    """Deletes a backup archive by filename."""
    backup_file = os.path.normpath(os.path.basename(filename))
    backup_file = os.path.join(backup_lib.BACKUPS_DIRNAME, backup_file)
    if not default_storage.exists(backup_file):
        raise NotFound("Unknown backup file.")
    default_storage.delete(backup_file)
    return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def logs(request):
    """Returns recent log records (newest first) from the redis log handler."""
    records = []
    error = None
    candidates = [logging.getLogger(), logging.getLogger("pykeg")]
    handlers = [h for logger_ in candidates for h in logger_.handlers]
    for handler in handlers:
        if isinstance(handler, RedisListHandler):
            try:
                records = list(handler.get_logs())
                records.reverse()
            except redis.RedisError as e:
                error = str(e) or "Unknown error."
            break
    return Response({"logs": records, "error": error})


@extend_schema(request=serializers.EmailTestRequestSerializer, responses=OpenApiTypes.BOOL)
@api_view(["POST"])
@permission_classes([permissions.IsAdminUser])
def email_test(request):
    """Sends a test notification email to the given address."""
    req = serializers.EmailTestRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    site = getattr(request, "kbsite", None) or models.KegbotSite.get()
    context = {
        "site_name": site.title,
        "site_url": site.base_url(),
        "settings_url": site.base_url() + "/account",
    }
    message = build_message(req.validated_data["address"], "notification/email_test.html", context)
    message.send(fail_silently=True)
    return Response(True)


@extend_schema(responses=OpenApiTypes.OBJECT)
@api_view(["GET"])
@permission_classes([permissions.IsAdminUser])
def bugreport(request):
    """Generates and returns a bugreport (may contain secrets; admin eyes only)."""
    out = io.StringIO()
    error = None
    try:
        bugreport_util.bugreport(out)
    except Exception as e:  # Never fail: partial output is still useful.
        logger.exception("Error generating bugreport")
        error = str(e)
    return Response({"output": out.getvalue(), "error": error})
