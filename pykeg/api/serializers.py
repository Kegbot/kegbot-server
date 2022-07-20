from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from pykeg.core import models


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

    def get_resized_url(self, picture):
        return picture.resized.url if picture else None

    def get_resized_png_url(self, picture):
        return picture.resized_png.url if picture else None

    def get_thumbnail_url(self, picture):
        return picture.thumbnail.url if picture else None

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

    background_image = PictureSerializer()
    stats = serializers.JSONField(source="get_stats")


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

    picture = PictureSerializer(source="mugshot")


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


class BeverageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Beverage
        fields = [
            "id",
            "name",
            "producer",
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

    producer = BeverageProducerSerializer()


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

    beverage = BeverageSerializer(source="type")
    illustration = serializers.URLField(source="get_illustration")
    illustration_thumbnail = serializers.URLField(source="get_illustration_thumb")
    stats = serializers.JSONField(source="get_stats")


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

    current_keg = KegSerializer()


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

    picture = PictureSerializer()
    user = UserSerializer()
    keg = KegSerializer()


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

    stats = serializers.JSONField(source="get_stats")


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

    drink = DrinkSerializer()
    keg = KegSerializer()
    user = UserSerializer()
    session = DrinkingSessionSerializer()


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


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        username = data["username"]
        password = data["password"]
        try:
            user = models.User.objects.get(username=username)
        except models.User.DoesNotExist:
            raise ValidationError("Incorrect username/password")
        if not user.check_password(password):
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

    picture = PictureSerializer(source="mugshot")


class SystemStatusSerializer(serializers.Serializer):
    """A summarized system status status, with the most common "current status" data."""

    site = KegbotSiteSerializer()
    taps = KegTapSerializer(many=True)
    events = SystemEventSerializer(many=True)
