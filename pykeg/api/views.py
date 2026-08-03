from django.conf import settings
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.views.decorators.csrf import ensure_csrf_cookie
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import (
    action,
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import (
    NotAuthenticated,
    NotFound,
    PermissionDenied,
    ValidationError,
)
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from pykeg.core import models

from . import filters, permissions, serializers


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all users in the system.

    Individual users (and their stats) are viewable by anyone the site
    privacy setting admits, mirroring the public drinker pages; the full
    user listing requires authentication.
    """

    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_class = filters.UserFilter
    lookup_field = "username"
    # Default lookup regex excludes ".", which usernames may contain.
    lookup_value_regex = "[^/]+"

    def get_permissions(self):
        if self.action in ("retrieve", "stats"):
            return [permissions.DashboardViewer()]
        return super().get_permissions()

    @extend_schema(responses=OpenApiTypes.OBJECT)
    @action(detail=True)
    def stats(self, request, username=None):
        """Returns the latest stats blob for this user."""
        return Response(self.get_object().get_stats())


class InvitationViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Lists all of the *current user's* invitations.

    Creating an invitation (when the site's registration mode allows the
    caller to invite) also sends the invitation e-mail.
    """

    queryset = models.Invitation.objects.all()
    serializer_class = serializers.InvitationSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                invited_by=self.request.user,
                invited_by__isnull=False,
            )
        )

    def perform_create(self, serializer):
        site = getattr(self.request, "kbsite", None) or models.KegbotSite.get()
        if not site.can_invite(self.request.user):
            raise PermissionDenied("You may not send invitations.")
        invitation = serializer.save(invited_by=self.request.user)
        invitation.send()


class DeviceViewSet(viewsets.ModelViewSet):
    """Lists all devices in the system.

    Admin-only view.
    """

    queryset = models.Device.objects.all()
    serializer_class = serializers.DeviceSerializer
    permission_classes = [permissions.IsAdminUser]


class ApiKeyViewSet(viewsets.ModelViewSet):
    """Lists a user's own api keys."""

    queryset = models.ApiKey.objects.all()
    serializer_class = serializers.ApiKeySerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                user=self.request.user,
                user__isnull=False,
            )
        )


class PictureAttachMixin:
    """Adds a POST {id}/picture action that sets the object's picture."""

    @extend_schema(request=serializers.PictureUploadRequestSerializer)
    @action(
        detail=True,
        methods=["post"],
        parser_classes=[MultiPartParser, FormParser],
    )
    def picture(self, request, pk=None):
        """Uploads and sets this object's picture."""
        obj = self.get_object()
        req = serializers.PictureUploadRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        obj.picture = models.Picture.objects.create(
            image=req.validated_data["image"],
            caption=req.validated_data["caption"],
        )
        obj.save(update_fields=["picture"])
        return Response(self.get_serializer(obj).data)


class BeverageProducerViewSet(PictureAttachMixin, viewsets.ModelViewSet):
    """Lists all beverage producers in the system."""

    queryset = models.BeverageProducer.objects.all()
    serializer_class = serializers.BeverageProducerSerializer
    permission_classes = [permissions.AdminWriteDashboardRead]


class BeverageViewSet(PictureAttachMixin, viewsets.ModelViewSet):
    """Lists all beverages in the system."""

    queryset = models.Beverage.objects.all()
    serializer_class = serializers.BeverageSerializer
    permission_classes = [permissions.AdminWriteDashboardRead]


class KegTapViewSet(viewsets.ModelViewSet):
    """Lists all KegTaps in the system.

    Reads follow site privacy; tap management (including the keg and
    hardware-connection operations below) requires an admin.
    """

    queryset = models.KegTap.objects.all()
    serializer_class = serializers.KegTapSerializer
    permission_classes = [permissions.AdminWriteDashboardRead]

    def _tap_response(self, tap):
        tap.refresh_from_db()
        return Response(self.get_serializer(tap).data)

    @extend_schema(
        request=serializers.TapAttachKegRequestSerializer,
        responses=serializers.KegTapSerializer,
    )
    @action(detail=True, methods=["post"], url_path="attach-keg")
    def attach_keg(self, request, pk=None):
        """Attaches an existing (available) keg to this tap."""
        tap = self.get_object()
        req = serializers.TapAttachKegRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        try:
            tap.attach_keg(req.validated_data["keg"])
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return self._tap_response(tap)

    @extend_schema(
        request=serializers.NewKegRequestSerializer,
        responses=serializers.KegTapSerializer,
    )
    @action(detail=True, methods=["post"], url_path="start-keg")
    def start_keg(self, request, pk=None):
        """Creates a new keg and attaches it to this tap."""
        tap = self.get_object()
        req = serializers.NewKegRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        params = req.validated_data
        try:
            models.Keg.start_keg(
                tap,
                beverage=params["beverage"],
                keg_type=params["keg_type"],
                full_volume_ml=params["full_volume_ml"],
                beverage_name=params["beverage_name"] or None,
                beverage_type=params["beverage_type"] if not params["beverage"] else None,
                producer_name=params["producer_name"] or None,
                style_name=params["style_name"] or None,
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return self._tap_response(tap)

    @extend_schema(request=None, responses=serializers.KegTapSerializer)
    @action(detail=True, methods=["post"], url_path="end-keg")
    def end_keg(self, request, pk=None):
        """Takes the tap's current keg offline."""
        tap = self.get_object()
        if not tap.current_keg:
            raise ValidationError("Tap has no active keg.")
        tap.end_current_keg()
        return self._tap_response(tap)

    @extend_schema(
        request=serializers.TapConnectMeterRequestSerializer,
        responses=serializers.KegTapSerializer,
    )
    @action(detail=True, methods=["post"], url_path="connect-meter")
    def connect_meter(self, request, pk=None):
        """Assigns a flow meter to this tap (null to disconnect)."""
        tap = self.get_object()
        req = serializers.TapConnectMeterRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        tap.connect_meter(req.validated_data["meter"])
        return self._tap_response(tap)

    @extend_schema(
        request=serializers.TapConnectToggleRequestSerializer,
        responses=serializers.KegTapSerializer,
    )
    @action(detail=True, methods=["post"], url_path="connect-toggle")
    def connect_toggle(self, request, pk=None):
        """Assigns a flow toggle to this tap (null to disconnect)."""
        tap = self.get_object()
        req = serializers.TapConnectToggleRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        tap.connect_toggle(req.validated_data["toggle"])
        return self._tap_response(tap)

    @extend_schema(
        request=serializers.TapConnectThermoRequestSerializer,
        responses=serializers.KegTapSerializer,
    )
    @action(detail=True, methods=["post"], url_path="connect-thermo")
    def connect_thermo(self, request, pk=None):
        """Assigns a temperature sensor to this tap (null to disconnect)."""
        tap = self.get_object()
        req = serializers.TapConnectThermoRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        tap.connect_thermo(req.validated_data["thermo_sensor"])
        return self._tap_response(tap)

    @extend_schema(
        request=serializers.TapRecordDrinkRequestSerializer,
        responses=serializers.DrinkSerializer,
    )
    @action(detail=True, methods=["post"], url_path="record-drink")
    def record_drink(self, request, pk=None):
        """Manually records a drink (or spill) against this tap's keg.

        Returns the new drink (201), or no content (204) when recorded
        as a spill.
        """
        tap = self.get_object()
        req = serializers.TapRecordDrinkRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        params = req.validated_data
        try:
            drink = models.Drink.record_drink(
                tap,
                ticks=0,
                volume_ml=params["volume_ml"],
                username=params["username"] or None,
                pour_time=params["pour_time"],
                duration=params["duration"],
                shout=params["shout"],
                spilled=params["spilled"],
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e
        if drink is None:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            serializers.DrinkSerializer(drink).data,
            status=status.HTTP_201_CREATED,
        )


class ControllerViewSet(viewsets.ModelViewSet):
    """Lists all Controllers in the system."""

    queryset = models.Controller.objects.all()
    serializer_class = serializers.ControllerSerializer
    permission_classes = [permissions.IsAdminUser]


class FlowMeterViewSet(viewsets.ModelViewSet):
    """Lists all FlowMeters in the system."""

    queryset = models.FlowMeter.objects.all()
    serializer_class = serializers.FlowMeterSerializer
    permission_classes = [permissions.IsAdminUser]


class FlowToggleViewSet(viewsets.ModelViewSet):
    """Lists all FlowToggles in the system."""

    queryset = models.FlowToggle.objects.all()
    serializer_class = serializers.FlowToggleSerializer
    permission_classes = [permissions.IsAdminUser]


class KegViewSet(viewsets.ModelViewSet):
    """Lists all Kegs in the system.

    Reads follow site privacy; keg management requires an admin. Deleting
    a keg permanently destroys it and ALL of its drinks.
    """

    queryset = models.Keg.objects.all()
    serializer_class = serializers.KegSerializer
    permission_classes = [permissions.AdminWriteDashboardRead]
    filterset_class = filters.KegFilter

    @extend_schema(request=serializers.KegCreateRequestSerializer)
    def create(self, request, *args, **kwargs):
        """Adds a new keg to the keg room (unattached)."""
        req = serializers.KegCreateRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        params = req.validated_data
        try:
            keg = models.Keg.create_keg(
                beverage=params["beverage"],
                keg_type=params["keg_type"],
                full_volume_ml=params["full_volume_ml"],
                beverage_name=params["beverage_name"] or None,
                beverage_type=params["beverage_type"] if not params["beverage"] else None,
                producer_name=params["producer_name"] or None,
                style_name=params["style_name"] or None,
                notes=params["notes"] or None,
                description=params["description"] or None,
            )
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(self.get_serializer(keg).data, status=status.HTTP_201_CREATED)

    def perform_destroy(self, instance):
        instance.cancel()

    @extend_schema(responses=OpenApiTypes.OBJECT)
    @action(detail=True)
    def stats(self, request, pk=None):
        """Returns the latest stats blob for this keg."""
        return Response(self.get_object().get_stats())

    @extend_schema(request=None, responses=serializers.KegSerializer)
    @action(detail=True, methods=["post"])
    def end(self, request, pk=None):
        """Marks an untapped keg as finished."""
        keg = self.get_object()
        try:
            keg.end_keg()
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(self.get_serializer(keg).data)

    @extend_schema(request=None, responses=serializers.KegSerializer)
    @action(detail=True, methods=["post"])
    def reactivate(self, request, pk=None):
        """Returns a finished keg to the available pool."""
        keg = self.get_object()
        try:
            keg.reactivate_keg()
        except ValueError as e:
            raise ValidationError(str(e)) from e
        return Response(self.get_serializer(keg).data)

    @extend_schema(
        request=serializers.KegSpillRequestSerializer,
        responses=serializers.KegSerializer,
    )
    @action(detail=True, methods=["post"])
    def spill(self, request, pk=None):
        """Records spilled volume against this keg."""
        keg = self.get_object()
        req = serializers.KegSpillRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        keg.spilled_ml += req.validated_data["volume_ml"]
        keg.save(update_fields=["spilled_ml"])
        return Response(self.get_serializer(keg).data)


class DrinkViewSet(
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Lists all Drinks in the system.

    Drinks are created by pours (or the tap record-drink endpoint), never
    directly. The drink's owner may edit its shout and manage its picture;
    volume adjustment, reassignment, and deletion are admin operations.
    """

    queryset = models.Drink.objects.all()
    serializer_class = serializers.DrinkSerializer
    permission_classes = [permissions.DashboardViewer]
    filterset_class = filters.DrinkFilter

    def get_permissions(self):
        if self.action in ("destroy", "reassign"):
            return [permissions.IsAdminUser()]
        if self.action in ("partial_update", "picture"):
            return [permissions.IsOwnerOrAdmin()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        """Cancels the drink; pass ?spilled=true to move its volume to spillage."""
        spilled = self.request.query_params.get("spilled") in ("1", "true")
        instance.cancel_drink(spilled=spilled)

    @extend_schema(
        request=serializers.DrinkUpdateRequestSerializer,
        responses=serializers.DrinkSerializer,
    )
    def partial_update(self, request, pk=None):
        drink = self.get_object()
        req = serializers.DrinkUpdateRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        data = req.validated_data
        if "volume_ml" in data and data["volume_ml"] != drink.volume_ml:
            if not request.user.is_staff:
                raise PermissionDenied("Only admins may adjust drink volume.")
            drink.set_volume(data["volume_ml"])
        if "shout" in data:
            drink.shout = data["shout"]
            drink.save(update_fields=["shout"])
        return Response(self.get_serializer(drink).data)

    @extend_schema(
        request=serializers.DrinkReassignRequestSerializer,
        responses=serializers.DrinkSerializer,
    )
    @action(detail=True, methods=["post"])
    def reassign(self, request, pk=None):
        """Reassigns this drink to another user."""
        drink = self.get_object()
        req = serializers.DrinkReassignRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        user = models.User.objects.get(username=req.validated_data["username"])
        drink.reassign(user)
        drink.refresh_from_db()
        return Response(self.get_serializer(drink).data)

    @extend_schema(
        request=serializers.PictureUploadRequestSerializer,
        responses=serializers.DrinkSerializer,
    )
    @action(
        detail=True,
        methods=["post", "delete"],
        parser_classes=[MultiPartParser, FormParser],
    )
    def picture(self, request, pk=None):
        """Attaches (POST) or erases (DELETE) this drink's picture."""
        drink = self.get_object()
        old_picture = drink.picture

        if request.method == "DELETE":
            if old_picture:
                old_picture.erase_and_delete()
                drink.refresh_from_db()
            return Response(status=status.HTTP_204_NO_CONTENT)

        req = serializers.PictureUploadRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        picture = models.Picture.objects.create(
            image=req.validated_data["image"],
            caption=req.validated_data["caption"],
            user=drink.user,
            keg=drink.keg,
            session=drink.session,
        )
        drink.picture = picture
        drink.save(update_fields=["picture"])
        if old_picture:
            old_picture.erase_and_delete()
        return Response(self.get_serializer(drink).data)


class AuthenticationTokenViewSet(viewsets.ModelViewSet):
    """Lists all AuthenticationTokens in the system."""

    queryset = models.AuthenticationToken.objects.all()
    serializer_class = serializers.AuthenticationTokenSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_class = filters.AuthenticationTokenFilter


class DrinkingSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all DrinkingSessions in the system."""

    queryset = models.DrinkingSession.objects.all()
    serializer_class = serializers.DrinkingSessionSerializer
    permission_classes = [permissions.DashboardViewer]
    filterset_class = filters.DrinkingSessionFilter

    @extend_schema(responses=serializers.DrinkingSessionSerializer)
    @action(detail=False)
    def current(self, request):
        """Returns the currently-active session, or 404 if there is none."""
        try:
            latest = models.DrinkingSession.objects.latest()
        except models.DrinkingSession.DoesNotExist:
            latest = None
        if not latest or not latest.IsActiveNow():
            raise NotFound("There is no active session.")
        return Response(self.get_serializer(latest).data)

    @extend_schema(responses=OpenApiTypes.OBJECT)
    @action(detail=True)
    def stats(self, request, pk=None):
        """Returns the latest stats blob for this session."""
        return Response(self.get_object().get_stats())


class ThermoSensorViewSet(viewsets.ModelViewSet):
    """Lists all ThermoSensors in the system."""

    queryset = models.ThermoSensor.objects.all()
    serializer_class = serializers.ThermoSensorSerializer
    permission_classes = [permissions.IsAdminUser]


class ThermologViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all Thermologs in the system."""

    queryset = models.Thermolog.objects.all()
    serializer_class = serializers.ThermologSerializer
    permission_classes = [permissions.DashboardViewer]
    filterset_class = filters.ThermologFilter


class StatsViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all stats snapshots in the system."""

    queryset = models.Stats.objects.all()
    serializer_class = serializers.StatsSerializer
    permission_classes = [permissions.DashboardViewer]

    @extend_schema(responses=OpenApiTypes.OBJECT)
    @action(detail=False)
    def system(self, request):
        """Returns the latest system-wide (all-time) stats blob."""
        site = getattr(request, "kbsite", None) or models.KegbotSite.get()
        return Response(site.get_stats())


class SystemEventViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all SystemEvents in the system."""

    queryset = models.SystemEvent.objects.all()
    serializer_class = serializers.SystemEventSerializer
    permission_classes = [permissions.DashboardViewer]
    filterset_class = filters.SystemEventFilter


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """Lists the *current user's* notification settings."""

    queryset = models.NotificationSettings.objects.all()
    serializer_class = serializers.NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PluginDataViewSet(viewsets.ModelViewSet):
    """Lists all PluginData in the system.

    Admin-only: plugin data may contain plugin credentials.
    """

    queryset = models.PluginData.objects.all()
    serializer_class = serializers.PluginDataSerializer
    permission_classes = [permissions.IsAdminUser]


@extend_schema(responses=serializers.SystemStatusSerializer)
@api_view(["GET"])
@permission_classes([permissions.DashboardViewer])
def system_status(request):
    """The 'current system status' view.

    Among other things, the `kegbot-frontend` uses this view to establish
    whether the system privacy permits reading from other APIs (status=200),
    or the user needs to log in (status=4xx), from application of the
    `DashboardViewer` permission
    """
    serializer = serializers.SystemStatusSerializer(
        instance={
            "site": request.kbsite,
            "taps": models.KegTap.objects.all(),
            "events": models.SystemEvent.objects.all().order_by("-id")[:20],
        }
    )
    return Response(serializer.data)


@extend_schema(request=serializers.LoginSerializer, responses=serializers.CurrentUserSerializer)
@api_view(["POST"])
@authentication_classes(())
@permission_classes(())
def login(request):
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    auth_login(request, user)
    return Response(serializers.CurrentUserSerializer(user).data)


@extend_schema(request=None, responses=OpenApiTypes.BOOL)
@api_view(["POST"])
def logout(request):
    auth_logout(request)
    return Response(True)


@ensure_csrf_cookie
@extend_schema(
    request=serializers.ProfileUpdateRequestSerializer, responses=serializers.MeSerializer
)
@api_view(["GET", "PATCH"])
@permission_classes(())
def me(request):
    """The frontend boot endpoint.

    GET always responds 200, regardless of authentication and site
    privacy: `user` is null for anonymous callers, and the rest of the
    payload is limited to privacy-safe configuration the frontend always
    needs (to render login screens, privacy interstitials, forms, and
    navigation). It also sets the CSRF cookie, so a fresh browser session
    can make authenticated POSTs after calling this.

    PATCH updates the current user's profile and returns the same payload.
    """
    if request.method == "PATCH":
        if not request.user.is_authenticated:
            raise NotAuthenticated()
        req = serializers.ProfileUpdateRequestSerializer(data=request.data)
        req.is_valid(raise_exception=True)
        if "display_name" in req.validated_data:
            request.user.display_name = req.validated_data["display_name"]
            request.user.save(update_fields=["display_name"])

    user = request.user if request.user.is_authenticated else None
    site = getattr(request, "kbsite", None) or models.KegbotSite.get()
    plugins = getattr(request, "plugins", {}) or {}
    payload = {
        "user": user,
        "site": site,
        "can_invite": site.can_invite(user),
        "have_sessions": models.DrinkingSession.objects.exists(),
        "sso_login_url": getattr(settings, "SSO_LOGIN_URL", "") or "",
        "sso_logout_url": getattr(settings, "SSO_LOGOUT_URL", "") or "",
        "plugins": [
            {"short_name": p.get_short_name(), "name": p.get_name()} for p in plugins.values()
        ],
    }
    return Response(serializers.MeSerializer(instance=payload).data)
