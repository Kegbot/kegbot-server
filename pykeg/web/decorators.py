from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test


def staff_member_required(view_func, redirect_field_name=REDIRECT_FIELD_NAME,
        login_url=settings.KEGBOT_ADMIN_LOGIN_URL):
    """
    Clone of django.contrib.admin.views.decorators.staff_member_required that
    uses `settings.KEGBOT_ADMIN_LOGIN_URL` as the default login URL.
    """
    return user_passes_test(
        lambda u: u.is_active and u.is_staff,
        login_url=login_url,
        redirect_field_name=redirect_field_name
    )(view_func)
