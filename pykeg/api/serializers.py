from django.contrib.auth import authenticate
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pykeg.core import kb_common, keg_sizes, models


class PictureSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Picture
        fields = [
            "id",
            "resized_url",
            "resized_png_url",
            "thumbnail_url",
            "thumbnail_png_url",
            "caption",
            "user_id",
            "keg_id",
            "session_id",
        ]

    resized_url = serializers.SerializerMethodField()
    resized_png_url = serializers.SerializerMethodField()
    thumbnail_url = serializers.SerializerMethodField()
    thumbnail_png_url = serializers.SerializerMethodField()
    caption = serializers.CharField()

    @extend_schema_field(OpenApiTypes.URI)
    def get_resized_url(self, picture):
        return picture.resized.url if picture else None

    @extend_schema_field(OpenApiTypes.URI)
    def get_resized_png_url(self, picture):
        return picture.resized_png.url if picture else None

    @extend_schema_field(OpenApiTypes.URI)
    def get_thumbnail_url(self, picture):
        return picture.thumbnail.url if picture else None

    @extend_schema_field(OpenApiTypes.URI)
    def get_thumbnail_png_url(self, picture):
        return picture.thumbnail_png.url if picture else None


class KegbotSiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KegbotSite
        fields = [
            "name",
            "server_version",
            "is_setup",
            "volume_display_units",
            "temperature_display_units",
            "title",
            "background_image",
            "google_analytics_id",
            "session_timeout_minutes",
            "privacy",
            "registration_mode",
            "timezone",
            "enable_sensing",
            "enable_users",
            "stats",
        ]

    background_image = PictureSerializer(read_only=True)
    stats = serializers.JSONField(source="get_stats", read_only=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "display_name",
            "is_staff",
            "is_active",
            "picture",
        ]
        read_only_fields = [
            "is_staff",
            "is_active",
        ]

    picture = PictureSerializer(source="mugshot", read_only=True)


class InvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Invitation
        fields = [
            "id",
            "for_email",
            "invited_date",
            "expires_date",
            "is_expired",
        ]

    is_expired = serializers.BooleanField(read_only=True)


class DeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Device
        fields = [
            "id",
            "name",
            "created_time",
        ]


class ApiKeySerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ApiKey
        fields = [
            "id",
            "user_id",
            "device_id",
            "is_active",
            "key",
            "description",
            "created_time",
        ]

    is_active = serializers.BooleanField(source="active")
    key = serializers.CharField(read_only=True)


class BeverageProducerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.BeverageProducer
        fields = [
            "id",
            "name",
            "country",
            "origin_state",
            "origin_city",
            "is_homebrew",
            "url",
            "description",
            "picture",
        ]

    picture = PictureSerializer(read_only=True)


class BeverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Beverage
        fields = [
            "id",
            "name",
            "producer",
            "producer_id",
            "beverage_type",
            "style",
            "description",
            "picture",
            "vintage_year",
            "abv_percent",
            "calories_per_ml",
            "carbs_per_ml",
            "color_hex",
            "original_gravity",
            "specific_gravity",
            "srm",
            "ibu",
            "star_rating",
            "untappd_beer_id",
        ]

    producer = BeverageProducerSerializer(read_only=True)
    producer_id = serializers.PrimaryKeyRelatedField(
        queryset=models.BeverageProducer.objects.all(), source="producer", write_only=True
    )
    picture = PictureSerializer(read_only=True)


class ControllerSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Controller
        fields = [
            "id",
            "name",
            "model_name",
            "serial_number",
        ]


class FlowMeterSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FlowMeter
        fields = [
            "id",
            "controller_id",
            "port_name",
            "tap_id",
            "ticks_per_ml",
        ]


class FlowToggleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.FlowToggle
        fields = [
            "id",
            "controller_id",
            "port_name",
            "tap_id",
        ]


class StatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Stats
        fields = [
            "time",
            "stats",
            "drink_id",
            "user_id",
            "keg_id",
            "session_id",
        ]


class KegSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Keg
        fields = [
            "id",
            "beverage",
            "keg_type",
            "served_volume_ml",
            "full_volume_ml",
            "start_time",
            "end_time",
            "status",
            "description",
            "spilled_ml",
            "notes",
            "illustration",
            "illustration_thumbnail",
            "stats",
        ]
        # Status and volumes change only through the keg lifecycle
        # endpoints (attach/end/reactivate/spill), never by direct edit.
        read_only_fields = [
            "status",
            "spilled_ml",
            "start_time",
            "end_time",
        ]

    beverage = BeverageSerializer(source="type", read_only=True)
    illustration = serializers.URLField(source="get_illustration", read_only=True)
    illustration_thumbnail = serializers.URLField(source="get_illustration_thumb", read_only=True)
    stats = serializers.JSONField(source="get_stats", read_only=True)


class KegTapSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.KegTap
        fields = [
            "id",
            "name",
            "notes",
            "current_keg_id",
            "temperature_sensor_id",
            "sort_order",
            "current_keg",
        ]

    current_keg = KegSerializer(read_only=True)
    # Connections change only through the attach-keg/connect-* endpoints.
    current_keg_id = serializers.IntegerField(read_only=True)
    temperature_sensor_id = serializers.IntegerField(read_only=True)


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Drink
        fields = [
            "id",
            "ticks",
            "volume_ml",
            "time",
            "duration",
            "user",
            "keg",
            "session_id",
            "shout",
            "picture",
        ]

    picture = PictureSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    keg = KegSerializer(read_only=True)


class AuthenticationTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.AuthenticationToken
        fields = [
            "id",
            "auth_device",
            "token_value",
            "nice_name",
            "pin",
            "user_id",
            "enabled",
            "created_time",
            "expire_time",
        ]


class DrinkingSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DrinkingSession
        fields = [
            "id",
            "start_time",
            "end_time",
            "volume_ml",
            "timezone",
            "name",
            "stats",
        ]

    stats = serializers.JSONField(source="get_stats", read_only=True)


class ThermoSensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ThermoSensor
        fields = [
            "id",
            "raw_name",
            "nice_name",
        ]


class ThermologSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Thermolog
        fields = [
            "time",
            "temp",
            "sensor_id",
        ]


class SystemEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.SystemEvent
        fields = [
            "id",
            "kind",
            "time",
            "drink",
            "user",
            "keg",
            "session",
        ]

    drink = DrinkSerializer(read_only=True)
    keg = KegSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    session = DrinkingSessionSerializer(read_only=True)


class NotificationSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.NotificationSettings
        fields = [
            "id",
            "user_id",
            "backend",
            "keg_tapped",
            "session_started",
            "keg_volume_low",
            "keg_ended",
        ]


class PluginDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PluginData
        fields = [
            "plugin_name",
            "key",
            "value",
        ]


class TapAttachKegRequestSerializer(serializers.Serializer):
    keg_id = serializers.PrimaryKeyRelatedField(queryset=models.Keg.objects.all(), source="keg")


class NewKegRequestSerializer(serializers.Serializer):
    """Parameters for creating a keg.

    The beverage may be given as an existing `beverage_id`, or described by
    the (`beverage_name`, `producer_name`, `style_name`, `beverage_type`)
    tuple, which matches or creates one.
    """

    beverage_id = serializers.PrimaryKeyRelatedField(
        queryset=models.Beverage.objects.all(),
        source="beverage",
        required=False,
        allow_null=True,
        default=None,
    )
    beverage_name = serializers.CharField(required=False, allow_blank=True, default="")
    beverage_type = serializers.ChoiceField(
        choices=models.Beverage.TYPES, required=False, default=models.Beverage.TYPE_BEER
    )
    producer_name = serializers.CharField(required=False, allow_blank=True, default="")
    style_name = serializers.CharField(required=False, allow_blank=True, default="")
    keg_type = serializers.ChoiceField(choices=keg_sizes.CHOICES, default=keg_sizes.HALF_BARREL)
    full_volume_ml = serializers.FloatField(required=False, allow_null=True, default=None)

    def validate(self, data):
        if not data.get("beverage") and not data.get("beverage_name"):
            raise ValidationError(
                "Give either beverage_id, or beverage_name with "
                "producer_name/style_name/beverage_type."
            )
        return data


class KegCreateRequestSerializer(NewKegRequestSerializer):
    description = serializers.CharField(required=False, allow_blank=True, default="")
    notes = serializers.CharField(required=False, allow_blank=True, default="")


class TapConnectMeterRequestSerializer(serializers.Serializer):
    meter_id = serializers.PrimaryKeyRelatedField(
        queryset=models.FlowMeter.objects.all(), source="meter", allow_null=True
    )


class TapConnectToggleRequestSerializer(serializers.Serializer):
    toggle_id = serializers.PrimaryKeyRelatedField(
        queryset=models.FlowToggle.objects.all(), source="toggle", allow_null=True
    )


class TapConnectThermoRequestSerializer(serializers.Serializer):
    thermo_sensor_id = serializers.PrimaryKeyRelatedField(
        queryset=models.ThermoSensor.objects.all(), source="thermo_sensor", allow_null=True
    )


class TapRecordDrinkRequestSerializer(serializers.Serializer):
    volume_ml = serializers.FloatField(min_value=0.0)
    username = serializers.CharField(required=False, allow_blank=True, default="")
    pour_time = serializers.DateTimeField(required=False, allow_null=True, default=None)
    duration = serializers.IntegerField(required=False, min_value=0, default=0)
    shout = serializers.CharField(required=False, allow_blank=True, default="")
    spilled = serializers.BooleanField(default=False)

    def validate_username(self, value):
        if value and not models.User.objects.filter(username=value).exists():
            raise ValidationError("No such user.")
        return value


class KegSpillRequestSerializer(serializers.Serializer):
    volume_ml = serializers.FloatField(min_value=0.0)


class DrinkUpdateRequestSerializer(serializers.Serializer):
    shout = serializers.CharField(required=False, allow_blank=True)
    volume_ml = serializers.FloatField(required=False, min_value=0.0)


class DrinkReassignRequestSerializer(serializers.Serializer):
    username = serializers.CharField()

    def validate_username(self, value):
        if not models.User.objects.filter(username=value).exists():
            raise ValidationError("No such user.")
        return value


class PictureUploadRequestSerializer(serializers.Serializer):
    image = serializers.ImageField()
    caption = serializers.CharField(required=False, allow_blank=True, default="")


class ProfileUpdateRequestSerializer(serializers.Serializer):
    display_name = serializers.CharField(required=False, allow_blank=True, max_length=127)


class PasswordChangeRequestSerializer(serializers.Serializer):
    current_password = serializers.CharField()
    new_password = serializers.CharField(min_length=1)


class EmailChangeRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class ConfirmEmailRequestSerializer(serializers.Serializer):
    token = serializers.CharField()


class ActivateAccountRequestSerializer(serializers.Serializer):
    activation_key = serializers.CharField()
    password = serializers.CharField(min_length=1)


class RegisterRequestSerializer(serializers.Serializer):
    username = serializers.RegexField(regex=kb_common.USERNAME_REGEX, max_length=30)
    email = serializers.EmailField()
    password = serializers.CharField(min_length=1)
    invite_code = serializers.CharField(required=False, allow_blank=True, default="")


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmRequestSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=1)


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data["username"], password=data["password"])
        if not user:
            raise ValidationError("Incorrect username/password")
        data["user"] = user
        return data


class CurrentUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.User
        fields = [
            "id",
            "username",
            "email",
            "display_name",
            "is_staff",
            "is_active",
            "picture",
        ]
        read_only_fields = [
            "is_staff",
            "is_active",
            "email",
        ]

    picture = PictureSerializer(source="mugshot", read_only=True)


class SystemStatusSerializer(serializers.Serializer):
    """A summarized system status status, with the most common "current status" data."""

    site = KegbotSiteSerializer()
    taps = KegTapSerializer(many=True)
    events = SystemEventSerializer(many=True)


class PluginInfoSerializer(serializers.Serializer):
    short_name = serializers.CharField()
    name = serializers.CharField()


class SiteConfigSerializer(serializers.ModelSerializer):
    """The privacy-safe subset of site settings, embedded in the boot payload.

    Unlike `KegbotSiteSerializer`, this contains no data derived from pours
    (no stats): it is served to anonymous users regardless of site privacy,
    since the frontend needs it to render the login and interstitial screens.
    """

    class Meta:
        model = models.KegbotSite
        fields = [
            "server_version",
            "title",
            "privacy",
            "registration_mode",
            "volume_display_units",
            "temperature_display_units",
            "timezone",
            "session_timeout_minutes",
            "enable_sensing",
            "enable_users",
            "google_analytics_id",
            "background_image",
        ]

    background_image = PictureSerializer(read_only=True)


class MeSerializer(serializers.Serializer):
    """The boot payload: current user plus always-needed site metadata.

    Served to every caller with status 200; `user` is null when the caller
    is not authenticated. Static constants (choice lists, keg sizes, and
    similar) are NOT served here: they are baked into the frontend build
    via the `print_constants` management command.
    """

    user = CurrentUserSerializer(allow_null=True)
    site = SiteConfigSerializer()
    can_invite = serializers.BooleanField()
    have_sessions = serializers.BooleanField()
    sso_login_url = serializers.CharField(allow_blank=True)
    sso_logout_url = serializers.CharField(allow_blank=True)
    plugins = PluginInfoSerializer(many=True)
