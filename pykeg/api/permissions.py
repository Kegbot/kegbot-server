import logging

from rest_framework import permissions

from pykeg.core import models

logger = logging.getLogger(__name__)

IsAdminUser = permissions.IsAdminUser


class DashboardViewer(permissions.BasePermission):
    """Default permission for API resources which respects site-privacy.

    Resources are readable without authentication, *unless* the site's
    `.privacy` setting is non-public.
    """

    message = "You must log in to do that"

    def has_permission(self, request, view):
        user = request.user
        if not request.kbsite:
            logger.warning("Cannot determine site")
            return False
        if request.kbsite.privacy == models.KegbotSite.PRIVACY_CHOICE_PUBLIC:
            return True
        elif request.kbsite.privacy == models.KegbotSite.PRIVACY_CHOICE_MEMBERS:
            return user.is_authenticated
        else:
            return user.is_staff


class IsAuthenticated(DashboardViewer):
    """Requires an authenticated user who also passes the site-privacy check."""

    message = "You must log in to do that"

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return bool(request.user and request.user.is_authenticated)


class AdminWriteDashboardRead(DashboardViewer):
    """Reads follow site-privacy; writes require a staff user."""

    message = "You must be an admin to do that"

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return super().has_permission(request, view)
        return bool(request.user and request.user.is_staff)


class IsOwnerOrAdmin(IsAuthenticated):
    """Requires the object's owning user (its `user` attribute) or an admin."""

    message = "You must own this object or be an admin to do that"

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return getattr(obj, "user", None) == request.user
