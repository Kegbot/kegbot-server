from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from rest_framework import viewsets
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.response import Response

from pykeg.core import models

from . import permissions, serializers


class UserViewSet(viewsets.ModelViewSet):
    """Lists all users in the system.

    Public view for any authenticated caller.
    """

    queryset = models.User.objects.all()
    serializer_class = serializers.UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class InvitationViewSet(viewsets.ModelViewSet):
    """Lists all of the *current user's* invitations."""

    queryset = models.Invitation.objects.all()
    serializer_class = serializers.UserSerializer
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

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(
                user=self.request.user,
                user__isnull=False,
            )
        )


class BeverageProducerViewSet(viewsets.ModelViewSet):
    """Lists all beverage producers in the system."""

    queryset = models.BeverageProducer.objects.all()
    serializer_class = serializers.BeverageProducerSerializer
    permission_classes = [permissions.IsAuthenticated]


class BeverageViewSet(viewsets.ModelViewSet):
    """Lists all beverages in the system."""

    queryset = models.Beverage.objects.all()
    serializer_class = serializers.BeverageSerializer
    permission_classes = [permissions.IsAuthenticated]


class KegTapViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all KegTaps in the system."""

    queryset = models.KegTap.objects.all()
    serializer_class = serializers.KegTapSerializer
    permission_classes = [permissions.DashboardViewer]


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


class KegViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all Kegs in the system."""

    queryset = models.Keg.objects.all()
    serializer_class = serializers.KegSerializer
    permission_classes = [permissions.DashboardViewer]


class DrinkViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all Drinks in the system."""

    queryset = models.Drink.objects.all()
    serializer_class = serializers.DrinkSerializer
    permission_classes = [permissions.DashboardViewer]


class AuthenticationTokenViewSet(viewsets.ModelViewSet):
    """Lists all AuthenticationTokens in the system."""

    queryset = models.AuthenticationToken.objects.all()
    serializer_class = serializers.AuthenticationTokenSerializer
    permission_classes = [permissions.IsAdminUser]


class DrinkingSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all DrinkingSessions in the system."""

    queryset = models.DrinkingSession.objects.all()
    serializer_class = serializers.DrinkingSessionSerializer
    permission_classes = [permissions.DashboardViewer]


class ThermoSensorViewSet(viewsets.ModelViewSet):
    """Lists all ThermoSensors in the system."""

    queryset = models.ThermoSensor.objects.all()
    serializer_class = serializers.ThermoSensorSerializer
    permission_classes = [permissions.IsAdminUser]


class ThermologViewSet(viewsets.ModelViewSet):
    """Lists all Thermologs in the system."""

    queryset = models.Thermolog.objects.all()
    serializer_class = serializers.ThermologSerializer
    permission_classes = [permissions.IsAdminUser]


class StatsViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all Statss in the system."""

    queryset = models.Stats.objects.all()
    serializer_class = serializers.StatsSerializer
    permission_classes = [permissions.DashboardViewer]


class SystemEventViewSet(viewsets.ReadOnlyModelViewSet):
    """Lists all SystemEvents in the system."""

    queryset = models.SystemEvent.objects.all()
    serializer_class = serializers.SystemEventSerializer
    permission_classes = [permissions.DashboardViewer]


class NotificationSettingsViewSet(viewsets.ModelViewSet):
    """Lists all NotificationSettingss in the system."""

    queryset = models.NotificationSettings.objects.all()
    serializer_class = serializers.NotificationSettingsSerializer
    permission_classes = [permissions.IsAuthenticated]


class PluginDataViewSet(viewsets.ModelViewSet):
    """Lists all PluginDatas in the system."""

    queryset = models.PluginData.objects.all()
    serializer_class = serializers.PluginDataSerializer
    permission_classes = [permissions.IsAuthenticated]


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


@api_view(["POST"])
@authentication_classes(())
@permission_classes(())
def login(request):
    serializer = serializers.LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data["user"]
    auth_login(request, user)
    return Response(serializers.CurrentUserSerializer(user).data)


@api_view(["POST"])
def logout(request):
    auth_logout(request)
    return Response(True)


@api_view(["GET"])
def current_user(request):
    user = request.user
    serializer = serializers.CurrentUserSerializer(instance=user)
    return Response(serializer.data)
