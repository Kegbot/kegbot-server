"""Setup wizard and upgrade endpoints.

These power the frontend's setup flow. They are reachable only while
setup or upgrade is required (`SetupAccess`), use no authenticators (the
database — including the session and user tables — may not exist yet),
and are exempted from the IsSetupMiddleware gate.

Unlike the old cookie-driven wizard, there is no server-side inter-step
state: the frontend collects choices and submits them in one settings
call.
"""

import io
import logging

from django.contrib.auth import authenticate
from django.contrib.auth import login as auth_login
from django.core import management
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from pykeg.core import defaults, models
from pykeg.core.util import get_version, get_version_object

from . import permissions, serializers

logger = logging.getLogger(__name__)


def _conflict(message):
    return Response({"detail": message}, status=status.HTTP_409_CONFLICT)


def setup_api_view(methods):
    """Composed decorators common to every setup endpoint."""

    def decorator(func):
        return api_view(methods)(
            authentication_classes(())(permission_classes([permissions.SetupAccess])(func))
        )

    return decorator


@extend_schema(responses=serializers.SetupStatusSerializer)
@setup_api_view(["GET"])
def setup_status(request):
    """Reports whether setup or upgrade is required."""
    payload = {
        "need_setup": request.need_setup,
        "need_upgrade": request.need_upgrade,
        "installed_version": getattr(request, "installed_version_string", None),
        "current_version": get_version(),
    }
    return Response(serializers.SetupStatusSerializer(instance=payload).data)


@extend_schema(request=None, responses=OpenApiTypes.OBJECT)
@setup_api_view(["POST"])
def migrate(request):
    """Creates or migrates the database (synchronous)."""
    out = io.StringIO()
    try:
        management.call_command("migrate", interactive=False, stdout=out)
    except Exception as e:
        logger.exception("Error migrating database")
        raise ValidationError({"detail": [str(e)]}) from e
    return Response({"output": out.getvalue()})


@extend_schema(
    request=serializers.SetupSiteSettingsRequestSerializer,
    responses=serializers.SetupSiteSettingsRequestSerializer,
)
@setup_api_view(["POST"])
def site_settings(request):
    """Applies initial site settings (after the database is migrated)."""
    if not request.need_setup:
        return _conflict("Site is already set up.")
    try:
        defaults.set_defaults()
    except defaults.AlreadyInstalledError:
        pass

    site = models.KegbotSite.get()
    serializer = serializers.SetupSiteSettingsRequestSerializer(
        site, data=request.data, partial=True
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)


@extend_schema(
    request=serializers.SetupAdminUserRequestSerializer,
    responses=serializers.CurrentUserSerializer,
)
@setup_api_view(["POST"])
def admin_user(request):
    """Creates the initial admin account and logs it in."""
    if not request.need_setup:
        return _conflict("Site is already set up.")
    req = serializers.SetupAdminUserRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    data = req.validated_data
    if models.User.objects.filter(username=data["username"]).exists():
        raise ValidationError({"username": ["A user with that username already exists."]})

    user = models.User(username=data["username"], email=data["email"])
    user.is_staff = True
    user.is_superuser = True
    user.set_password(data["password"])
    user.save()

    # By this point the session table exists (migrated in the first step),
    # so the new admin can be logged in for the rest of the flow.
    user = authenticate(username=data["username"], password=data["password"])
    auth_login(request, user)
    return Response(serializers.CurrentUserSerializer(user).data, status=status.HTTP_201_CREATED)


@extend_schema(request=None, responses=OpenApiTypes.BOOL)
@setup_api_view(["POST"])
def finish(request):
    """Marks setup complete."""
    if not request.need_setup:
        return _conflict("Site is already set up.")
    site = models.KegbotSite.get()
    site.is_setup = True
    site.server_version = str(get_version_object())
    site.save()
    return Response(True)


@extend_schema(request=None, responses=OpenApiTypes.OBJECT)
@setup_api_view(["POST"])
def upgrade(request):
    """Migrates the database and stamps the current server version."""
    if not request.need_upgrade:
        return _conflict("No upgrade is required.")
    out = io.StringIO()
    try:
        management.call_command("migrate", interactive=False, stdout=out)
        site = models.KegbotSite.get()
        site.server_version = str(get_version_object())
        site.save()
    except Exception as e:
        logger.exception("Error upgrading database")
        raise ValidationError({"detail": [str(e)]}) from e
    return Response({"output": out.getvalue()})
