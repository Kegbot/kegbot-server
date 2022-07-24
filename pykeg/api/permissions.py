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
    """Permission for API resources which respects site-privacy.

    Resources are readable without authentication, *unless* the site's
    `.privacy` setting is non-public.
    """

    message = "You must log in to do that"

    def has_permission(self, request, view):
        if not super().has_permission(request, view):
            return False
        return bool(request.user and request.user.is_authenticated)
