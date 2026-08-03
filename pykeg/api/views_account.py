"""Account self-service and authentication-flow endpoints.

These replace the server-rendered account, registration, and password
management pages. Endpoints that operate before login (register, password
reset, activation) are unauthenticated and rate-limited.
"""

from django.contrib.auth import authenticate, update_session_auth_hash
from django.contrib.auth import login as auth_login
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    parser_classes,
    permission_classes,
    throttle_classes,
)
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle

from pykeg.core import models
from pykeg.util import email as email_util
from pykeg.web.auth import UserExistsException
from pykeg.web.kbregistration.forms import PasswordResetForm

from . import serializers


class AuthAttemptThrottle(AnonRateThrottle):
    scope = "auth"


@extend_schema(request=serializers.PasswordChangeRequestSerializer, responses=OpenApiTypes.BOOL)
@api_view(["POST"])
def change_password(request):
    """Changes the current user's password, keeping the session valid."""
    req = serializers.PasswordChangeRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    data = req.validated_data
    if not request.user.check_password(data["current_password"]):
        raise ValidationError({"current_password": ["Incorrect password."]})
    request.user.set_password(data["new_password"])
    request.user.save()
    update_session_auth_hash(request, request.user)
    return Response(True)


@extend_schema(request=serializers.EmailChangeRequestSerializer, responses=OpenApiTypes.BOOL)
@api_view(["POST"])
def change_email(request):
    """Requests an email change; a confirmation link is mailed to the new address."""
    req = serializers.EmailChangeRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    new_email = req.validated_data["email"]
    if new_email == request.user.email:
        raise ValidationError({"email": ["E-mail address unchanged."]})

    site = getattr(request, "kbsite", None) or models.KegbotSite.get()
    token = email_util.build_email_change_token(request.user, new_email)
    url = site.reverse_full("account-confirm-email", args=(), kwargs={"token": token})
    message = email_util.build_message(
        new_email,
        "registration/email_confirm_email_change.html",
        {"url": url, "site_name": site.title},
    )
    message.send()
    return Response(True)


@extend_schema(
    request=serializers.ConfirmEmailRequestSerializer,
    responses=serializers.CurrentUserSerializer,
)
@api_view(["POST"])
def confirm_email(request):
    """Applies an email change, given the token from the confirmation mail."""
    req = serializers.ConfirmEmailRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    try:
        uid, new_address = email_util.verify_email_change_token(
            request.user, req.validated_data["token"]
        )
    except ValueError:
        raise ValidationError({"token": ["That token is not valid."]}) from None
    if uid != request.user.id:
        raise ValidationError({"token": ["E-mail confirmation does not exist for this account."]})
    if request.user.email != new_address:
        request.user.email = new_address
        request.user.save()
    return Response(serializers.CurrentUserSerializer(request.user).data)


@extend_schema(
    request=serializers.PictureUploadRequestSerializer,
    responses=serializers.CurrentUserSerializer,
)
@api_view(["POST"])
@parser_classes([MultiPartParser, FormParser])
def mugshot(request):
    """Sets the current user's mugshot."""
    req = serializers.PictureUploadRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    picture = models.Picture.objects.create(image=req.validated_data["image"], user=request.user)
    request.user.mugshot = picture
    request.user.save()
    return Response(serializers.CurrentUserSerializer(request.user).data)


@extend_schema(request=None, responses=serializers.ApiKeySerializer)
@api_view(["POST"])
def regenerate_api_key(request):
    """Discards and regenerates the current user's API key."""
    key, _ = models.ApiKey.objects.get_or_create(user=request.user)
    key.regenerate()
    return Response(serializers.ApiKeySerializer(key).data)


@extend_schema(
    request=serializers.ActivateAccountRequestSerializer,
    responses=serializers.CurrentUserSerializer,
)
@api_view(["POST"])
@authentication_classes(())
@permission_classes(())
@throttle_classes([AuthAttemptThrottle])
def activate(request):
    """Activates an invited/created account: sets its password and logs in."""
    req = serializers.ActivateAccountRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    data = req.validated_data
    users = models.User.objects.filter(activation_key=data["activation_key"])
    if users.count() != 1:
        raise NotFound("No such activation key.")
    user = users[0]
    if user.has_usable_password():
        raise ValidationError({"activation_key": ["Account is already activated."]})

    user.set_password(data["password"])
    user.activation_key = None
    user.save()

    user = authenticate(username=user.username, password=data["password"])
    auth_login(request, user)
    return Response(serializers.CurrentUserSerializer(user).data)


@extend_schema(
    request=serializers.RegisterRequestSerializer,
    responses=serializers.CurrentUserSerializer,
)
@api_view(["POST"])
@authentication_classes(())
@permission_classes(())
@throttle_classes([AuthAttemptThrottle])
def register(request):
    """Registers a new account, honoring the site's registration mode."""
    site = getattr(request, "kbsite", None) or models.KegbotSite.get()
    req = serializers.RegisterRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    data = req.validated_data

    invite = None
    if site.registration_mode != "public":
        invite_code = data.get("invite_code") or ""
        if not invite_code:
            raise PermissionDenied("An invitation is required to register.")
        invite = models.Invitation.objects.filter(invite_code=invite_code).first()
        if not invite or invite.is_expired():
            raise PermissionDenied("Invitation is invalid or expired.")

    try:
        models.User.create_new_user(
            username=data["username"], email=data["email"], password=data["password"]
        )
    except UserExistsException:
        raise ValidationError({"username": ["A user with that username already exists."]}) from None

    if invite:
        invite.delete()

    user = authenticate(username=data["username"], password=data["password"])
    auth_login(request, user)
    return Response(serializers.CurrentUserSerializer(user).data, status=201)


@extend_schema(request=serializers.PasswordResetRequestSerializer, responses=OpenApiTypes.BOOL)
@api_view(["POST"])
@authentication_classes(())
@permission_classes(())
@throttle_classes([AuthAttemptThrottle])
def password_reset(request):
    """Mails a password-reset link. Always succeeds (no account enumeration)."""
    req = serializers.PasswordResetRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    form = PasswordResetForm({"email": req.validated_data["email"]})
    if form.is_valid():
        form.save(request=request)
    return Response(True)


@extend_schema(
    request=serializers.PasswordResetConfirmRequestSerializer, responses=OpenApiTypes.BOOL
)
@api_view(["POST"])
@authentication_classes(())
@permission_classes(())
@throttle_classes([AuthAttemptThrottle])
def password_reset_confirm(request):
    """Sets a new password, given the uid/token pair from a reset mail."""
    req = serializers.PasswordResetConfirmRequestSerializer(data=request.data)
    req.is_valid(raise_exception=True)
    data = req.validated_data
    try:
        uid = force_str(urlsafe_base64_decode(data["uid"]))
        user = models.User.objects.get(pk=uid)
    except TypeError, ValueError, OverflowError, models.User.DoesNotExist:
        raise ValidationError({"token": ["Invalid password reset link."]}) from None
    if not default_token_generator.check_token(user, data["token"]):
        raise ValidationError({"token": ["Invalid or expired password reset link."]})
    user.set_password(data["new_password"])
    user.save()
    return Response(True)
