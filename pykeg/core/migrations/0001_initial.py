# -*- coding: utf-8 -*-

from django.db import models, migrations
import pykeg.core.fields
import pykeg.core.models
import django.db.models.deletion
import re
import django.utils.timezone
from django.conf import settings
import django.core.validators
import pykeg.core.jsonfield


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("password", models.CharField(max_length=128, verbose_name="password")),
                (
                    "last_login",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="last login"
                    ),
                ),
                (
                    "is_superuser",
                    models.BooleanField(
                        default=False,
                        help_text="Designates that this user has all permissions without explicitly assigning them.",
                        verbose_name="superuser status",
                    ),
                ),
                (
                    "username",
                    models.CharField(
                        help_text="Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters",
                        unique=True,
                        max_length=30,
                        verbose_name="username",
                        validators=[
                            django.core.validators.RegexValidator(
                                re.compile("^[\\w.@+-]+$"), "Enter a valid username.", "invalid"
                            )
                        ],
                    ),
                ),
                (
                    "display_name",
                    models.CharField(
                        default="",
                        help_text="Full name, will be shown in some places instead of username",
                        max_length=127,
                    ),
                ),
                (
                    "email",
                    models.EmailField(max_length=75, verbose_name="email address", blank=True),
                ),
                (
                    "is_staff",
                    models.BooleanField(
                        default=False,
                        help_text="Designates whether the user can log into this admin site.",
                        verbose_name="staff status",
                    ),
                ),
                (
                    "is_active",
                    models.BooleanField(
                        default=True,
                        help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                        verbose_name="active",
                    ),
                ),
                (
                    "date_joined",
                    models.DateTimeField(
                        default=django.utils.timezone.now, verbose_name="date joined"
                    ),
                ),
                (
                    "activation_key",
                    models.CharField(
                        help_text="Unguessable token, used to finish registration.",
                        max_length=128,
                        null=True,
                        blank=True,
                    ),
                ),
            ],
            options={
                "verbose_name": "user",
                "verbose_name_plural": "users",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ApiKey",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "key",
                    models.CharField(
                        default=pykeg.core.models.get_default_api_key,
                        help_text="The secret key.",
                        unique=True,
                        max_length=127,
                        editable=False,
                    ),
                ),
                (
                    "active",
                    models.BooleanField(
                        default=True, help_text="Whether access by this key is currently allowed."
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Information about this key.", null=True, blank=True
                    ),
                ),
                (
                    "created_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now, help_text="Time the key was created."
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="AuthenticationToken",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "auth_device",
                    models.CharField(help_text="Namespace for this token.", max_length=64),
                ),
                (
                    "token_value",
                    models.CharField(
                        help_text="Actual value of the token, unique within an auth_device.",
                        max_length=128,
                    ),
                ),
                (
                    "nice_name",
                    models.CharField(
                        help_text='A human-readable alias for the token, for example "Guest Key".',
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "pin",
                    models.CharField(
                        help_text="A secret value necessary to authenticate with this token.",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True, help_text="Whether this token is considered active."
                    ),
                ),
                (
                    "created_time",
                    models.DateTimeField(
                        help_text="Date token was first added to the system.", auto_now_add=True
                    ),
                ),
                (
                    "expire_time",
                    models.DateTimeField(
                        help_text="Date after which token is treated as disabled.",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="tokens",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        help_text="User in possession of and authenticated by this token.",
                        null=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Beverage",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text='Name of the beverage, such as "Potrero Pale".', max_length=255
                    ),
                ),
                (
                    "beverage_type",
                    models.CharField(
                        default="beer",
                        max_length=32,
                        choices=[
                            ("beer", "Beer"),
                            ("wine", "Wine"),
                            ("soda", "Soda"),
                            ("kombucha", "Kombucha"),
                            ("other", "Other/Unknown"),
                        ],
                    ),
                ),
                (
                    "style",
                    models.CharField(
                        help_text='Beverage style within type, eg "Pale Ale", "Pinot Noir".',
                        max_length=255,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="Free-form description of the beverage.", null=True, blank=True
                    ),
                ),
                (
                    "vintage_year",
                    models.DateField(
                        help_text="Date of production, for wines or special/seasonal editions",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "abv_percent",
                    models.FloatField(
                        help_text="Alcohol by volume, as percentage (0.0-100.0).",
                        null=True,
                        verbose_name="ABV Percentage",
                        blank=True,
                    ),
                ),
                (
                    "calories_per_ml",
                    models.FloatField(
                        help_text="Calories per mL of beverage.", null=True, blank=True
                    ),
                ),
                (
                    "carbs_per_ml",
                    models.FloatField(
                        help_text="Carbohydrates per mL of beverage.", null=True, blank=True
                    ),
                ),
                (
                    "color_hex",
                    models.CharField(
                        default="#C35900",
                        help_text="Approximate beverage color",
                        max_length=16,
                        verbose_name="Color (Hex Value)",
                        validators=[
                            django.core.validators.RegexValidator(
                                regex="(^#[0-9a-zA-Z]{3}$)|(^#[0-9a-zA-Z]{6}$)",
                                message='Color must start with "#" and include 3 or 6 hex characters, like #123 or #123456.',
                                code="bad_color",
                            )
                        ],
                    ),
                ),
                (
                    "original_gravity",
                    models.FloatField(
                        help_text="Original gravity (beer only).", null=True, blank=True
                    ),
                ),
                (
                    "specific_gravity",
                    models.FloatField(
                        help_text="Final gravity (beer only).", null=True, blank=True
                    ),
                ),
                (
                    "srm",
                    models.FloatField(
                        help_text="Standard Reference Method value (beer only).",
                        null=True,
                        verbose_name="SRM Value",
                        blank=True,
                    ),
                ),
                (
                    "ibu",
                    models.FloatField(
                        help_text="International Bittering Units value (beer only).",
                        null=True,
                        verbose_name="IBUs",
                        blank=True,
                    ),
                ),
                (
                    "star_rating",
                    models.FloatField(
                        blank=True,
                        help_text="Star rating for beverage (0: worst, 5: best)",
                        null=True,
                        validators=[
                            django.core.validators.MinValueValidator(0.0),
                            django.core.validators.MaxValueValidator(5.0),
                        ],
                    ),
                ),
                (
                    "untappd_beer_id",
                    models.IntegerField(
                        help_text="Untappd.com resource ID (beer only).", null=True, blank=True
                    ),
                ),
                (
                    "beverage_backend",
                    models.CharField(
                        help_text="Future use.", max_length=255, null=True, blank=True
                    ),
                ),
                (
                    "beverage_backend_id",
                    models.CharField(
                        help_text="Future use.", max_length=255, null=True, blank=True
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="BeverageProducer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(help_text="Name of the brewer", max_length=255)),
                (
                    "country",
                    pykeg.core.fields.CountryField(
                        default="USA",
                        help_text="Country of origin",
                        max_length=3,
                        choices=[
                            ("AFG", "Afghanistan"),
                            ("ALA", "Aland Islands"),
                            ("ALB", "Albania"),
                            ("DZA", "Algeria"),
                            ("ASM", "American Samoa"),
                            ("AND", "Andorra"),
                            ("AGO", "Angola"),
                            ("AIA", "Anguilla"),
                            ("ATG", "Antigua and Barbuda"),
                            ("ARG", "Argentina"),
                            ("ARM", "Armenia"),
                            ("ABW", "Aruba"),
                            ("AUS", "Australia"),
                            ("AUT", "Austria"),
                            ("AZE", "Azerbaijan"),
                            ("BHS", "Bahamas"),
                            ("BHR", "Bahrain"),
                            ("BGD", "Bangladesh"),
                            ("BRB", "Barbados"),
                            ("BLR", "Belarus"),
                            ("BEL", "Belgium"),
                            ("BLZ", "Belize"),
                            ("BEN", "Benin"),
                            ("BMU", "Bermuda"),
                            ("BTN", "Bhutan"),
                            ("BOL", "Bolivia"),
                            ("BIH", "Bosnia and Herzegovina"),
                            ("BWA", "Botswana"),
                            ("BRA", "Brazil"),
                            ("VGB", "British Virgin Islands"),
                            ("BRN", "Brunei Darussalam"),
                            ("BGR", "Bulgaria"),
                            ("BFA", "Burkina Faso"),
                            ("BDI", "Burundi"),
                            ("KHM", "Cambodia"),
                            ("CMR", "Cameroon"),
                            ("CAN", "Canada"),
                            ("CPV", "Cape Verde"),
                            ("CYM", "Cayman Islands"),
                            ("CAF", "Central African Republic"),
                            ("TCD", "Chad"),
                            ("CIL", "Channel Islands"),
                            ("CHL", "Chile"),
                            ("CHN", "China"),
                            ("HKG", "China - Hong Kong"),
                            ("MAC", "China - Macao"),
                            ("COL", "Colombia"),
                            ("COM", "Comoros"),
                            ("COG", "Congo"),
                            ("COK", "Cook Islands"),
                            ("CRI", "Costa Rica"),
                            ("CIV", "Cote d'Ivoire"),
                            ("HRV", "Croatia"),
                            ("CUB", "Cuba"),
                            ("CYP", "Cyprus"),
                            ("CZE", "Czech Republic"),
                            ("PRK", "Democratic People's Republic of Korea"),
                            ("COD", "Democratic Republic of the Congo"),
                            ("DNK", "Denmark"),
                            ("DJI", "Djibouti"),
                            ("DMA", "Dominica"),
                            ("DOM", "Dominican Republic"),
                            ("ECU", "Ecuador"),
                            ("EGY", "Egypt"),
                            ("SLV", "El Salvador"),
                            ("GNQ", "Equatorial Guinea"),
                            ("ERI", "Eritrea"),
                            ("EST", "Estonia"),
                            ("ETH", "Ethiopia"),
                            ("FRO", "Faeroe Islands"),
                            ("FLK", "Falkland Islands (Malvinas)"),
                            ("FJI", "Fiji"),
                            ("FIN", "Finland"),
                            ("FRA", "France"),
                            ("GUF", "French Guiana"),
                            ("PYF", "French Polynesia"),
                            ("GAB", "Gabon"),
                            ("GMB", "Gambia"),
                            ("GEO", "Georgia"),
                            ("DEU", "Germany"),
                            ("GHA", "Ghana"),
                            ("GIB", "Gibraltar"),
                            ("GRC", "Greece"),
                            ("GRL", "Greenland"),
                            ("GRD", "Grenada"),
                            ("GLP", "Guadeloupe"),
                            ("GUM", "Guam"),
                            ("GTM", "Guatemala"),
                            ("GGY", "Guernsey"),
                            ("GIN", "Guinea"),
                            ("GNB", "Guinea-Bissau"),
                            ("GUY", "Guyana"),
                            ("HTI", "Haiti"),
                            ("VAT", "Holy See (Vatican City)"),
                            ("HND", "Honduras"),
                            ("HUN", "Hungary"),
                            ("ISL", "Iceland"),
                            ("IND", "India"),
                            ("IDN", "Indonesia"),
                            ("IRN", "Iran"),
                            ("IRQ", "Iraq"),
                            ("IRL", "Ireland"),
                            ("IMN", "Isle of Man"),
                            ("ISR", "Israel"),
                            ("ITA", "Italy"),
                            ("JAM", "Jamaica"),
                            ("JPN", "Japan"),
                            ("JEY", "Jersey"),
                            ("JOR", "Jordan"),
                            ("KAZ", "Kazakhstan"),
                            ("KEN", "Kenya"),
                            ("KIR", "Kiribati"),
                            ("KWT", "Kuwait"),
                            ("KGZ", "Kyrgyzstan"),
                            ("LAO", "Lao People's Democratic Republic"),
                            ("LVA", "Latvia"),
                            ("LBN", "Lebanon"),
                            ("LSO", "Lesotho"),
                            ("LBR", "Liberia"),
                            ("LBY", "Libyan Arab Jamahiriya"),
                            ("LIE", "Liechtenstein"),
                            ("LTU", "Lithuania"),
                            ("LUX", "Luxembourg"),
                            ("MKD", "Macedonia"),
                            ("MDG", "Madagascar"),
                            ("MWI", "Malawi"),
                            ("MYS", "Malaysia"),
                            ("MDV", "Maldives"),
                            ("MLI", "Mali"),
                            ("MLT", "Malta"),
                            ("MHL", "Marshall Islands"),
                            ("MTQ", "Martinique"),
                            ("MRT", "Mauritania"),
                            ("MUS", "Mauritius"),
                            ("MYT", "Mayotte"),
                            ("MEX", "Mexico"),
                            ("FSM", "Micronesia, Federated States of"),
                            ("MCO", "Monaco"),
                            ("MNG", "Mongolia"),
                            ("MNE", "Montenegro"),
                            ("MSR", "Montserrat"),
                            ("MAR", "Morocco"),
                            ("MOZ", "Mozambique"),
                            ("MMR", "Myanmar"),
                            ("NAM", "Namibia"),
                            ("NRU", "Nauru"),
                            ("NPL", "Nepal"),
                            ("NLD", "Netherlands"),
                            ("ANT", "Netherlands Antilles"),
                            ("NCL", "New Caledonia"),
                            ("NZL", "New Zealand"),
                            ("NIC", "Nicaragua"),
                            ("NER", "Niger"),
                            ("NGA", "Nigeria"),
                            ("NIU", "Niue"),
                            ("NFK", "Norfolk Island"),
                            ("MNP", "Northern Mariana Islands"),
                            ("NOR", "Norway"),
                            ("PSE", "Occupied Palestinian Territory"),
                            ("OMN", "Oman"),
                            ("PAK", "Pakistan"),
                            ("PLW", "Palau"),
                            ("PAN", "Panama"),
                            ("PNG", "Papua New Guinea"),
                            ("PRY", "Paraguay"),
                            ("PER", "Peru"),
                            ("PHL", "Philippines"),
                            ("PCN", "Pitcairn"),
                            ("POL", "Poland"),
                            ("PRT", "Portugal"),
                            ("PRI", "Puerto Rico"),
                            ("QAT", "Qatar"),
                            ("KOR", "Republic of Korea"),
                            ("MDA", "Republic of Moldova"),
                            ("REU", "Reunion"),
                            ("ROU", "Romania"),
                            ("RUS", "Russian Federation"),
                            ("RWA", "Rwanda"),
                            ("BLM", "Saint-Barthelemy"),
                            ("SHN", "Saint Helena"),
                            ("KNA", "Saint Kitts and Nevis"),
                            ("LCA", "Saint Lucia"),
                            ("MAF", "Saint-Martin (French part)"),
                            ("SPM", "Saint Pierre and Miquelon"),
                            ("VCT", "Saint Vincent and the Grenadines"),
                            ("WSM", "Samoa"),
                            ("SMR", "San Marino"),
                            ("STP", "Sao Tome and Principe"),
                            ("SAU", "Saudi Arabia"),
                            ("SEN", "Senegal"),
                            ("SRB", "Serbia"),
                            ("SYC", "Seychelles"),
                            ("SLE", "Sierra Leone"),
                            ("SGP", "Singapore"),
                            ("SVK", "Slovakia"),
                            ("SVN", "Slovenia"),
                            ("SLB", "Solomon Islands"),
                            ("SOM", "Somalia"),
                            ("ZAF", "South Africa"),
                            ("ESP", "Spain"),
                            ("LKA", "Sri Lanka"),
                            ("SDN", "Sudan"),
                            ("SUR", "Suriname"),
                            ("SJM", "Svalbard and Jan Mayen Islands"),
                            ("SWZ", "Swaziland"),
                            ("SWE", "Sweden"),
                            ("CHE", "Switzerland"),
                            ("SYR", "Syrian Arab Republic"),
                            ("TJK", "Tajikistan"),
                            ("THA", "Thailand"),
                            ("TLS", "Timor-Leste"),
                            ("TGO", "Togo"),
                            ("TKL", "Tokelau"),
                            ("TON", "Tonga"),
                            ("TTO", "Trinidad and Tobago"),
                            ("TUN", "Tunisia"),
                            ("TUR", "Turkey"),
                            ("TKM", "Turkmenistan"),
                            ("TCA", "Turks and Caicos Islands"),
                            ("TUV", "Tuvalu"),
                            ("UGA", "Uganda"),
                            ("UKR", "Ukraine"),
                            ("ARE", "United Arab Emirates"),
                            ("GBR", "United Kingdom"),
                            ("TZA", "United Republic of Tanzania"),
                            ("USA", "United States of America"),
                            ("VIR", "United States Virgin Islands"),
                            ("URY", "Uruguay"),
                            ("UZB", "Uzbekistan"),
                            ("VUT", "Vanuatu"),
                            ("VEN", "Venezuela (Bolivarian Republic of)"),
                            ("VNM", "Viet Nam"),
                            ("WLF", "Wallis and Futuna Islands"),
                            ("ESH", "Western Sahara"),
                            ("YEM", "Yemen"),
                            ("ZMB", "Zambia"),
                            ("ZWE", "Zimbabwe"),
                        ],
                    ),
                ),
                (
                    "origin_state",
                    models.CharField(
                        default="",
                        max_length=128,
                        null=True,
                        help_text="State of origin, if applicable",
                        blank=True,
                    ),
                ),
                (
                    "origin_city",
                    models.CharField(
                        default="",
                        max_length=128,
                        null=True,
                        help_text="City of origin, if known",
                        blank=True,
                    ),
                ),
                ("is_homebrew", models.BooleanField(default=False)),
                (
                    "url",
                    models.URLField(
                        default="", null=True, help_text="Brewer's home page", blank=True
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        default="",
                        help_text="A short description of the brewer",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "beverage_backend",
                    models.CharField(
                        help_text="Future use.", max_length=255, null=True, blank=True
                    ),
                ),
                (
                    "beverage_backend_id",
                    models.CharField(
                        help_text="Future use.", max_length=255, null=True, blank=True
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Controller",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Identifying name for this device; must be unique.",
                        unique=True,
                        max_length=128,
                    ),
                ),
                (
                    "model_name",
                    models.CharField(
                        help_text="Type of controller (optional).",
                        max_length=128,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "serial_number",
                    models.CharField(
                        help_text="Serial number (optional).",
                        max_length=128,
                        null=True,
                        blank=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Device",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("name", models.CharField(default="Unknown Device", max_length=255)),
                (
                    "created_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now, help_text="Time the device was created."
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Drink",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "ticks",
                    models.PositiveIntegerField(
                        help_text="Flow sensor ticks, never changed once recorded.", editable=False
                    ),
                ),
                (
                    "volume_ml",
                    models.FloatField(
                        help_text="Calculated (or set) Drink volume.", editable=False
                    ),
                ),
                ("time", models.DateTimeField(help_text="Date and time of pour.", editable=False)),
                (
                    "duration",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Time in seconds taken to pour this Drink.",
                        editable=False,
                        blank=True,
                    ),
                ),
                (
                    "shout",
                    models.TextField(
                        help_text="Comment from the drinker at the time of the pour.",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "tick_time_series",
                    models.TextField(
                        help_text="Tick update sequence that generated this drink (diagnostic data).",
                        null=True,
                        editable=False,
                        blank=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-time",),
                "get_latest_by": "time",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="DrinkingSession",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("start_time", models.DateTimeField()),
                ("end_time", models.DateTimeField()),
                ("volume_ml", models.FloatField(default=0)),
                ("name", models.CharField(max_length=256, null=True, blank=True)),
            ],
            options={
                "ordering": ("-start_time",),
                "get_latest_by": "start_time",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FlowMeter",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "port_name",
                    models.CharField(
                        help_text="Controller-specific data port name for this meter.",
                        max_length=128,
                    ),
                ),
                (
                    "ticks_per_ml",
                    models.FloatField(
                        default=2.724,
                        help_text="Flow meter pulses per mL of fluid.  Common values: 2.724 (FT330-RJ), 5.4 (SF800)",
                    ),
                ),
                (
                    "controller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="meters",
                        to="core.Controller",
                        help_text="Controller that owns this meter.",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="FlowToggle",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "port_name",
                    models.CharField(
                        help_text="Controller-specific data port name for this toggle.",
                        max_length=128,
                    ),
                ),
                (
                    "controller",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="toggles",
                        to="core.Controller",
                        help_text="Controller that owns this toggle.",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Invitation",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "invite_code",
                    models.CharField(
                        default=pykeg.core.models.get_default_invite_code,
                        help_text="Unguessable token which must be presented to use this invite",
                        unique=True,
                        max_length=255,
                    ),
                ),
                (
                    "for_email",
                    models.EmailField(
                        help_text="Address this invitation was sent to.", max_length=75
                    ),
                ),
                (
                    "invited_date",
                    models.DateTimeField(
                        help_text="Date and time the invitation was sent",
                        verbose_name="date invited",
                        auto_now_add=True,
                    ),
                ),
                (
                    "expires_date",
                    models.DateTimeField(
                        default=pykeg.core.models.get_default_expires_date,
                        help_text="Date and time after which the invitation is considered expired",
                        verbose_name="date expries",
                    ),
                ),
                (
                    "invited_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.AUTH_USER_MODEL,
                        help_text="User that created this invitation, if any.",
                        null=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Keg",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "keg_type",
                    models.CharField(
                        default="half-barrel",
                        help_text="Keg container type, used to initialize keg's full volume",
                        max_length=32,
                        choices=[
                            ("quarter", "Quarter Barrel (7.75 gal)"),
                            ("corny", "Corny Keg (5 gal)"),
                            ("sixth", "Sixth Barrel (5.17 gal)"),
                            ("other", "Other"),
                            ("euro-half", "European Half Barrel (50 L)"),
                            ("half-barrel", "Half Barrel (15.5 gal)"),
                            ("euro", "European Full Barrel (100 L)"),
                        ],
                    ),
                ),
                (
                    "served_volume_ml",
                    models.FloatField(
                        default=0, help_text="Computed served volume.", editable=False
                    ),
                ),
                (
                    "full_volume_ml",
                    models.FloatField(
                        default=0,
                        help_text="Full volume of this Keg; usually set automatically from keg_type.",
                        editable=False,
                    ),
                ),
                (
                    "start_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Time the Keg was first tapped.",
                    ),
                ),
                (
                    "end_time",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        help_text="Time the Keg was finished or disconnected.",
                    ),
                ),
                (
                    "online",
                    models.BooleanField(
                        default=True,
                        help_text="True if the keg is currently assigned to a tap.",
                        editable=False,
                    ),
                ),
                (
                    "finished",
                    models.BooleanField(
                        default=False,
                        help_text="True when the Keg has been exhausted or discarded.",
                        editable=False,
                    ),
                ),
                (
                    "description",
                    models.CharField(
                        help_text="User-visible description of the Keg.",
                        max_length=256,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "spilled_ml",
                    models.FloatField(
                        default=0,
                        help_text="Amount of beverage poured without an associated Drink.",
                    ),
                ),
                (
                    "notes",
                    models.TextField(
                        help_text="Private notes about this keg, viewable only by admins.",
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "type",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        to="core.Beverage",
                        help_text="Beverage in this Keg.",
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="KegbotSite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "name",
                    models.CharField(default="default", unique=True, max_length=64, editable=False),
                ),
                ("server_version", models.CharField(max_length=64, null=True, editable=False)),
                (
                    "is_setup",
                    models.BooleanField(
                        default=False,
                        help_text="True if the site has completed setup.",
                        editable=False,
                    ),
                ),
                (
                    "registration_id",
                    models.TextField(
                        default="",
                        help_text="A unique id for this system.",
                        max_length=128,
                        editable=False,
                        blank=True,
                    ),
                ),
                (
                    "volume_display_units",
                    models.CharField(
                        default="imperial",
                        help_text="Unit system to use when displaying volumetric data.",
                        max_length=64,
                        choices=[
                            ("metric", "Metric (mL, L)"),
                            ("imperial", "Imperial (oz, pint)"),
                        ],
                    ),
                ),
                (
                    "temperature_display_units",
                    models.CharField(
                        default="f",
                        help_text="Unit system to use when displaying temperature data.",
                        max_length=64,
                        choices=[("f", "Fahrenheit"), ("c", "Celsius")],
                    ),
                ),
                (
                    "title",
                    models.CharField(
                        default="My Kegbot", help_text="The title of this site.", max_length=64
                    ),
                ),
                (
                    "google_analytics_id",
                    models.CharField(
                        help_text="Set to your Google Analytics ID to enable tracking. Example: UA-XXXX-y",
                        max_length=64,
                        null=True,
                        blank=True,
                    ),
                ),
                (
                    "session_timeout_minutes",
                    models.PositiveIntegerField(
                        default=180,
                        help_text="Maximum time, in minutes, that a session may be idle (no pours) before it is considered to be finished.  Recommended value is 180.",
                    ),
                ),
                (
                    "privacy",
                    models.CharField(
                        default="public",
                        help_text="Who can view Kegbot data?",
                        max_length=63,
                        choices=[
                            ("public", "Public: Browsing does not require login"),
                            ("members", "Members only: Must log in to browse"),
                            ("staff", "Staff only: Only logged-in staff accounts may browse"),
                        ],
                    ),
                ),
                (
                    "registration_mode",
                    models.CharField(
                        default="public",
                        help_text="Who can join this Kegbot from the web site?",
                        max_length=63,
                        choices=[
                            ("public", "Public: Anyone can register."),
                            (
                                "member-invite-only",
                                "Member Invite: Must be invited by an existing member.",
                            ),
                            (
                                "staff-invite-only",
                                "Staff Invite Only: Must be invited by a staff member.",
                            ),
                        ],
                    ),
                ),
                (
                    "timezone",
                    models.CharField(
                        default="UTC",
                        help_text="Time zone for this system.",
                        max_length=255,
                        choices=[
                            ("Africa/Abidjan", "Africa/Abidjan"),
                            ("Africa/Accra", "Africa/Accra"),
                            ("Africa/Addis_Ababa", "Africa/Addis_Ababa"),
                            ("Africa/Algiers", "Africa/Algiers"),
                            ("Africa/Asmara", "Africa/Asmara"),
                            ("Africa/Bamako", "Africa/Bamako"),
                            ("Africa/Bangui", "Africa/Bangui"),
                            ("Africa/Banjul", "Africa/Banjul"),
                            ("Africa/Bissau", "Africa/Bissau"),
                            ("Africa/Blantyre", "Africa/Blantyre"),
                            ("Africa/Brazzaville", "Africa/Brazzaville"),
                            ("Africa/Bujumbura", "Africa/Bujumbura"),
                            ("Africa/Cairo", "Africa/Cairo"),
                            ("Africa/Casablanca", "Africa/Casablanca"),
                            ("Africa/Ceuta", "Africa/Ceuta"),
                            ("Africa/Conakry", "Africa/Conakry"),
                            ("Africa/Dakar", "Africa/Dakar"),
                            ("Africa/Dar_es_Salaam", "Africa/Dar_es_Salaam"),
                            ("Africa/Djibouti", "Africa/Djibouti"),
                            ("Africa/Douala", "Africa/Douala"),
                            ("Africa/El_Aaiun", "Africa/El_Aaiun"),
                            ("Africa/Freetown", "Africa/Freetown"),
                            ("Africa/Gaborone", "Africa/Gaborone"),
                            ("Africa/Harare", "Africa/Harare"),
                            ("Africa/Johannesburg", "Africa/Johannesburg"),
                            ("Africa/Juba", "Africa/Juba"),
                            ("Africa/Kampala", "Africa/Kampala"),
                            ("Africa/Khartoum", "Africa/Khartoum"),
                            ("Africa/Kigali", "Africa/Kigali"),
                            ("Africa/Kinshasa", "Africa/Kinshasa"),
                            ("Africa/Lagos", "Africa/Lagos"),
                            ("Africa/Libreville", "Africa/Libreville"),
                            ("Africa/Lome", "Africa/Lome"),
                            ("Africa/Luanda", "Africa/Luanda"),
                            ("Africa/Lubumbashi", "Africa/Lubumbashi"),
                            ("Africa/Lusaka", "Africa/Lusaka"),
                            ("Africa/Malabo", "Africa/Malabo"),
                            ("Africa/Maputo", "Africa/Maputo"),
                            ("Africa/Maseru", "Africa/Maseru"),
                            ("Africa/Mbabane", "Africa/Mbabane"),
                            ("Africa/Mogadishu", "Africa/Mogadishu"),
                            ("Africa/Monrovia", "Africa/Monrovia"),
                            ("Africa/Nairobi", "Africa/Nairobi"),
                            ("Africa/Ndjamena", "Africa/Ndjamena"),
                            ("Africa/Niamey", "Africa/Niamey"),
                            ("Africa/Nouakchott", "Africa/Nouakchott"),
                            ("Africa/Ouagadougou", "Africa/Ouagadougou"),
                            ("Africa/Porto-Novo", "Africa/Porto-Novo"),
                            ("Africa/Sao_Tome", "Africa/Sao_Tome"),
                            ("Africa/Tripoli", "Africa/Tripoli"),
                            ("Africa/Tunis", "Africa/Tunis"),
                            ("Africa/Windhoek", "Africa/Windhoek"),
                            ("America/Adak", "America/Adak"),
                            ("America/Anchorage", "America/Anchorage"),
                            ("America/Anguilla", "America/Anguilla"),
                            ("America/Antigua", "America/Antigua"),
                            ("America/Araguaina", "America/Araguaina"),
                            ("America/Argentina/Buenos_Aires", "America/Argentina/Buenos_Aires"),
                            ("America/Argentina/Catamarca", "America/Argentina/Catamarca"),
                            ("America/Argentina/Cordoba", "America/Argentina/Cordoba"),
                            ("America/Argentina/Jujuy", "America/Argentina/Jujuy"),
                            ("America/Argentina/La_Rioja", "America/Argentina/La_Rioja"),
                            ("America/Argentina/Mendoza", "America/Argentina/Mendoza"),
                            ("America/Argentina/Rio_Gallegos", "America/Argentina/Rio_Gallegos"),
                            ("America/Argentina/Salta", "America/Argentina/Salta"),
                            ("America/Argentina/San_Juan", "America/Argentina/San_Juan"),
                            ("America/Argentina/San_Luis", "America/Argentina/San_Luis"),
                            ("America/Argentina/Tucuman", "America/Argentina/Tucuman"),
                            ("America/Argentina/Ushuaia", "America/Argentina/Ushuaia"),
                            ("America/Aruba", "America/Aruba"),
                            ("America/Asuncion", "America/Asuncion"),
                            ("America/Atikokan", "America/Atikokan"),
                            ("America/Bahia", "America/Bahia"),
                            ("America/Bahia_Banderas", "America/Bahia_Banderas"),
                            ("America/Barbados", "America/Barbados"),
                            ("America/Belem", "America/Belem"),
                            ("America/Belize", "America/Belize"),
                            ("America/Blanc-Sablon", "America/Blanc-Sablon"),
                            ("America/Boa_Vista", "America/Boa_Vista"),
                            ("America/Bogota", "America/Bogota"),
                            ("America/Boise", "America/Boise"),
                            ("America/Cambridge_Bay", "America/Cambridge_Bay"),
                            ("America/Campo_Grande", "America/Campo_Grande"),
                            ("America/Cancun", "America/Cancun"),
                            ("America/Caracas", "America/Caracas"),
                            ("America/Cayenne", "America/Cayenne"),
                            ("America/Cayman", "America/Cayman"),
                            ("America/Chicago", "America/Chicago"),
                            ("America/Chihuahua", "America/Chihuahua"),
                            ("America/Costa_Rica", "America/Costa_Rica"),
                            ("America/Creston", "America/Creston"),
                            ("America/Cuiaba", "America/Cuiaba"),
                            ("America/Curacao", "America/Curacao"),
                            ("America/Danmarkshavn", "America/Danmarkshavn"),
                            ("America/Dawson", "America/Dawson"),
                            ("America/Dawson_Creek", "America/Dawson_Creek"),
                            ("America/Denver", "America/Denver"),
                            ("America/Detroit", "America/Detroit"),
                            ("America/Dominica", "America/Dominica"),
                            ("America/Edmonton", "America/Edmonton"),
                            ("America/Eirunepe", "America/Eirunepe"),
                            ("America/El_Salvador", "America/El_Salvador"),
                            ("America/Fortaleza", "America/Fortaleza"),
                            ("America/Glace_Bay", "America/Glace_Bay"),
                            ("America/Godthab", "America/Godthab"),
                            ("America/Goose_Bay", "America/Goose_Bay"),
                            ("America/Grand_Turk", "America/Grand_Turk"),
                            ("America/Grenada", "America/Grenada"),
                            ("America/Guadeloupe", "America/Guadeloupe"),
                            ("America/Guatemala", "America/Guatemala"),
                            ("America/Guayaquil", "America/Guayaquil"),
                            ("America/Guyana", "America/Guyana"),
                            ("America/Halifax", "America/Halifax"),
                            ("America/Havana", "America/Havana"),
                            ("America/Hermosillo", "America/Hermosillo"),
                            ("America/Indiana/Indianapolis", "America/Indiana/Indianapolis"),
                            ("America/Indiana/Knox", "America/Indiana/Knox"),
                            ("America/Indiana/Marengo", "America/Indiana/Marengo"),
                            ("America/Indiana/Petersburg", "America/Indiana/Petersburg"),
                            ("America/Indiana/Tell_City", "America/Indiana/Tell_City"),
                            ("America/Indiana/Vevay", "America/Indiana/Vevay"),
                            ("America/Indiana/Vincennes", "America/Indiana/Vincennes"),
                            ("America/Indiana/Winamac", "America/Indiana/Winamac"),
                            ("America/Inuvik", "America/Inuvik"),
                            ("America/Iqaluit", "America/Iqaluit"),
                            ("America/Jamaica", "America/Jamaica"),
                            ("America/Juneau", "America/Juneau"),
                            ("America/Kentucky/Louisville", "America/Kentucky/Louisville"),
                            ("America/Kentucky/Monticello", "America/Kentucky/Monticello"),
                            ("America/Kralendijk", "America/Kralendijk"),
                            ("America/La_Paz", "America/La_Paz"),
                            ("America/Lima", "America/Lima"),
                            ("America/Los_Angeles", "America/Los_Angeles"),
                            ("America/Lower_Princes", "America/Lower_Princes"),
                            ("America/Maceio", "America/Maceio"),
                            ("America/Managua", "America/Managua"),
                            ("America/Manaus", "America/Manaus"),
                            ("America/Marigot", "America/Marigot"),
                            ("America/Martinique", "America/Martinique"),
                            ("America/Matamoros", "America/Matamoros"),
                            ("America/Mazatlan", "America/Mazatlan"),
                            ("America/Menominee", "America/Menominee"),
                            ("America/Merida", "America/Merida"),
                            ("America/Metlakatla", "America/Metlakatla"),
                            ("America/Mexico_City", "America/Mexico_City"),
                            ("America/Miquelon", "America/Miquelon"),
                            ("America/Moncton", "America/Moncton"),
                            ("America/Monterrey", "America/Monterrey"),
                            ("America/Montevideo", "America/Montevideo"),
                            ("America/Montreal", "America/Montreal"),
                            ("America/Montserrat", "America/Montserrat"),
                            ("America/Nassau", "America/Nassau"),
                            ("America/New_York", "America/New_York"),
                            ("America/Nipigon", "America/Nipigon"),
                            ("America/Nome", "America/Nome"),
                            ("America/Noronha", "America/Noronha"),
                            ("America/North_Dakota/Beulah", "America/North_Dakota/Beulah"),
                            ("America/North_Dakota/Center", "America/North_Dakota/Center"),
                            ("America/North_Dakota/New_Salem", "America/North_Dakota/New_Salem"),
                            ("America/Ojinaga", "America/Ojinaga"),
                            ("America/Panama", "America/Panama"),
                            ("America/Pangnirtung", "America/Pangnirtung"),
                            ("America/Paramaribo", "America/Paramaribo"),
                            ("America/Phoenix", "America/Phoenix"),
                            ("America/Port-au-Prince", "America/Port-au-Prince"),
                            ("America/Port_of_Spain", "America/Port_of_Spain"),
                            ("America/Porto_Velho", "America/Porto_Velho"),
                            ("America/Puerto_Rico", "America/Puerto_Rico"),
                            ("America/Rainy_River", "America/Rainy_River"),
                            ("America/Rankin_Inlet", "America/Rankin_Inlet"),
                            ("America/Recife", "America/Recife"),
                            ("America/Regina", "America/Regina"),
                            ("America/Resolute", "America/Resolute"),
                            ("America/Rio_Branco", "America/Rio_Branco"),
                            ("America/Santa_Isabel", "America/Santa_Isabel"),
                            ("America/Santarem", "America/Santarem"),
                            ("America/Santiago", "America/Santiago"),
                            ("America/Santo_Domingo", "America/Santo_Domingo"),
                            ("America/Sao_Paulo", "America/Sao_Paulo"),
                            ("America/Scoresbysund", "America/Scoresbysund"),
                            ("America/Sitka", "America/Sitka"),
                            ("America/St_Barthelemy", "America/St_Barthelemy"),
                            ("America/St_Johns", "America/St_Johns"),
                            ("America/St_Kitts", "America/St_Kitts"),
                            ("America/St_Lucia", "America/St_Lucia"),
                            ("America/St_Thomas", "America/St_Thomas"),
                            ("America/St_Vincent", "America/St_Vincent"),
                            ("America/Swift_Current", "America/Swift_Current"),
                            ("America/Tegucigalpa", "America/Tegucigalpa"),
                            ("America/Thule", "America/Thule"),
                            ("America/Thunder_Bay", "America/Thunder_Bay"),
                            ("America/Tijuana", "America/Tijuana"),
                            ("America/Toronto", "America/Toronto"),
                            ("America/Tortola", "America/Tortola"),
                            ("America/Vancouver", "America/Vancouver"),
                            ("America/Whitehorse", "America/Whitehorse"),
                            ("America/Winnipeg", "America/Winnipeg"),
                            ("America/Yakutat", "America/Yakutat"),
                            ("America/Yellowknife", "America/Yellowknife"),
                            ("Antarctica/Casey", "Antarctica/Casey"),
                            ("Antarctica/Davis", "Antarctica/Davis"),
                            ("Antarctica/DumontDUrville", "Antarctica/DumontDUrville"),
                            ("Antarctica/Macquarie", "Antarctica/Macquarie"),
                            ("Antarctica/Mawson", "Antarctica/Mawson"),
                            ("Antarctica/McMurdo", "Antarctica/McMurdo"),
                            ("Antarctica/Palmer", "Antarctica/Palmer"),
                            ("Antarctica/Rothera", "Antarctica/Rothera"),
                            ("Antarctica/Syowa", "Antarctica/Syowa"),
                            ("Antarctica/Troll", "Antarctica/Troll"),
                            ("Antarctica/Vostok", "Antarctica/Vostok"),
                            ("Arctic/Longyearbyen", "Arctic/Longyearbyen"),
                            ("Asia/Aden", "Asia/Aden"),
                            ("Asia/Almaty", "Asia/Almaty"),
                            ("Asia/Amman", "Asia/Amman"),
                            ("Asia/Anadyr", "Asia/Anadyr"),
                            ("Asia/Aqtau", "Asia/Aqtau"),
                            ("Asia/Aqtobe", "Asia/Aqtobe"),
                            ("Asia/Ashgabat", "Asia/Ashgabat"),
                            ("Asia/Baghdad", "Asia/Baghdad"),
                            ("Asia/Bahrain", "Asia/Bahrain"),
                            ("Asia/Baku", "Asia/Baku"),
                            ("Asia/Bangkok", "Asia/Bangkok"),
                            ("Asia/Beirut", "Asia/Beirut"),
                            ("Asia/Bishkek", "Asia/Bishkek"),
                            ("Asia/Brunei", "Asia/Brunei"),
                            ("Asia/Choibalsan", "Asia/Choibalsan"),
                            ("Asia/Chongqing", "Asia/Chongqing"),
                            ("Asia/Colombo", "Asia/Colombo"),
                            ("Asia/Damascus", "Asia/Damascus"),
                            ("Asia/Dhaka", "Asia/Dhaka"),
                            ("Asia/Dili", "Asia/Dili"),
                            ("Asia/Dubai", "Asia/Dubai"),
                            ("Asia/Dushanbe", "Asia/Dushanbe"),
                            ("Asia/Gaza", "Asia/Gaza"),
                            ("Asia/Harbin", "Asia/Harbin"),
                            ("Asia/Hebron", "Asia/Hebron"),
                            ("Asia/Ho_Chi_Minh", "Asia/Ho_Chi_Minh"),
                            ("Asia/Hong_Kong", "Asia/Hong_Kong"),
                            ("Asia/Hovd", "Asia/Hovd"),
                            ("Asia/Irkutsk", "Asia/Irkutsk"),
                            ("Asia/Jakarta", "Asia/Jakarta"),
                            ("Asia/Jayapura", "Asia/Jayapura"),
                            ("Asia/Jerusalem", "Asia/Jerusalem"),
                            ("Asia/Kabul", "Asia/Kabul"),
                            ("Asia/Kamchatka", "Asia/Kamchatka"),
                            ("Asia/Karachi", "Asia/Karachi"),
                            ("Asia/Kashgar", "Asia/Kashgar"),
                            ("Asia/Kathmandu", "Asia/Kathmandu"),
                            ("Asia/Khandyga", "Asia/Khandyga"),
                            ("Asia/Kolkata", "Asia/Kolkata"),
                            ("Asia/Krasnoyarsk", "Asia/Krasnoyarsk"),
                            ("Asia/Kuala_Lumpur", "Asia/Kuala_Lumpur"),
                            ("Asia/Kuching", "Asia/Kuching"),
                            ("Asia/Kuwait", "Asia/Kuwait"),
                            ("Asia/Macau", "Asia/Macau"),
                            ("Asia/Magadan", "Asia/Magadan"),
                            ("Asia/Makassar", "Asia/Makassar"),
                            ("Asia/Manila", "Asia/Manila"),
                            ("Asia/Muscat", "Asia/Muscat"),
                            ("Asia/Nicosia", "Asia/Nicosia"),
                            ("Asia/Novokuznetsk", "Asia/Novokuznetsk"),
                            ("Asia/Novosibirsk", "Asia/Novosibirsk"),
                            ("Asia/Omsk", "Asia/Omsk"),
                            ("Asia/Oral", "Asia/Oral"),
                            ("Asia/Phnom_Penh", "Asia/Phnom_Penh"),
                            ("Asia/Pontianak", "Asia/Pontianak"),
                            ("Asia/Pyongyang", "Asia/Pyongyang"),
                            ("Asia/Qatar", "Asia/Qatar"),
                            ("Asia/Qyzylorda", "Asia/Qyzylorda"),
                            ("Asia/Rangoon", "Asia/Rangoon"),
                            ("Asia/Riyadh", "Asia/Riyadh"),
                            ("Asia/Sakhalin", "Asia/Sakhalin"),
                            ("Asia/Samarkand", "Asia/Samarkand"),
                            ("Asia/Seoul", "Asia/Seoul"),
                            ("Asia/Shanghai", "Asia/Shanghai"),
                            ("Asia/Singapore", "Asia/Singapore"),
                            ("Asia/Taipei", "Asia/Taipei"),
                            ("Asia/Tashkent", "Asia/Tashkent"),
                            ("Asia/Tbilisi", "Asia/Tbilisi"),
                            ("Asia/Tehran", "Asia/Tehran"),
                            ("Asia/Thimphu", "Asia/Thimphu"),
                            ("Asia/Tokyo", "Asia/Tokyo"),
                            ("Asia/Ulaanbaatar", "Asia/Ulaanbaatar"),
                            ("Asia/Urumqi", "Asia/Urumqi"),
                            ("Asia/Ust-Nera", "Asia/Ust-Nera"),
                            ("Asia/Vientiane", "Asia/Vientiane"),
                            ("Asia/Vladivostok", "Asia/Vladivostok"),
                            ("Asia/Yakutsk", "Asia/Yakutsk"),
                            ("Asia/Yekaterinburg", "Asia/Yekaterinburg"),
                            ("Asia/Yerevan", "Asia/Yerevan"),
                            ("Atlantic/Azores", "Atlantic/Azores"),
                            ("Atlantic/Bermuda", "Atlantic/Bermuda"),
                            ("Atlantic/Canary", "Atlantic/Canary"),
                            ("Atlantic/Cape_Verde", "Atlantic/Cape_Verde"),
                            ("Atlantic/Faroe", "Atlantic/Faroe"),
                            ("Atlantic/Madeira", "Atlantic/Madeira"),
                            ("Atlantic/Reykjavik", "Atlantic/Reykjavik"),
                            ("Atlantic/South_Georgia", "Atlantic/South_Georgia"),
                            ("Atlantic/St_Helena", "Atlantic/St_Helena"),
                            ("Atlantic/Stanley", "Atlantic/Stanley"),
                            ("Australia/Adelaide", "Australia/Adelaide"),
                            ("Australia/Brisbane", "Australia/Brisbane"),
                            ("Australia/Broken_Hill", "Australia/Broken_Hill"),
                            ("Australia/Currie", "Australia/Currie"),
                            ("Australia/Darwin", "Australia/Darwin"),
                            ("Australia/Eucla", "Australia/Eucla"),
                            ("Australia/Hobart", "Australia/Hobart"),
                            ("Australia/Lindeman", "Australia/Lindeman"),
                            ("Australia/Lord_Howe", "Australia/Lord_Howe"),
                            ("Australia/Melbourne", "Australia/Melbourne"),
                            ("Australia/Perth", "Australia/Perth"),
                            ("Australia/Sydney", "Australia/Sydney"),
                            ("Canada/Atlantic", "Canada/Atlantic"),
                            ("Canada/Central", "Canada/Central"),
                            ("Canada/Eastern", "Canada/Eastern"),
                            ("Canada/Mountain", "Canada/Mountain"),
                            ("Canada/Newfoundland", "Canada/Newfoundland"),
                            ("Canada/Pacific", "Canada/Pacific"),
                            ("Europe/Amsterdam", "Europe/Amsterdam"),
                            ("Europe/Andorra", "Europe/Andorra"),
                            ("Europe/Athens", "Europe/Athens"),
                            ("Europe/Belgrade", "Europe/Belgrade"),
                            ("Europe/Berlin", "Europe/Berlin"),
                            ("Europe/Bratislava", "Europe/Bratislava"),
                            ("Europe/Brussels", "Europe/Brussels"),
                            ("Europe/Bucharest", "Europe/Bucharest"),
                            ("Europe/Budapest", "Europe/Budapest"),
                            ("Europe/Busingen", "Europe/Busingen"),
                            ("Europe/Chisinau", "Europe/Chisinau"),
                            ("Europe/Copenhagen", "Europe/Copenhagen"),
                            ("Europe/Dublin", "Europe/Dublin"),
                            ("Europe/Gibraltar", "Europe/Gibraltar"),
                            ("Europe/Guernsey", "Europe/Guernsey"),
                            ("Europe/Helsinki", "Europe/Helsinki"),
                            ("Europe/Isle_of_Man", "Europe/Isle_of_Man"),
                            ("Europe/Istanbul", "Europe/Istanbul"),
                            ("Europe/Jersey", "Europe/Jersey"),
                            ("Europe/Kaliningrad", "Europe/Kaliningrad"),
                            ("Europe/Kiev", "Europe/Kiev"),
                            ("Europe/Lisbon", "Europe/Lisbon"),
                            ("Europe/Ljubljana", "Europe/Ljubljana"),
                            ("Europe/London", "Europe/London"),
                            ("Europe/Luxembourg", "Europe/Luxembourg"),
                            ("Europe/Madrid", "Europe/Madrid"),
                            ("Europe/Malta", "Europe/Malta"),
                            ("Europe/Mariehamn", "Europe/Mariehamn"),
                            ("Europe/Minsk", "Europe/Minsk"),
                            ("Europe/Monaco", "Europe/Monaco"),
                            ("Europe/Moscow", "Europe/Moscow"),
                            ("Europe/Oslo", "Europe/Oslo"),
                            ("Europe/Paris", "Europe/Paris"),
                            ("Europe/Podgorica", "Europe/Podgorica"),
                            ("Europe/Prague", "Europe/Prague"),
                            ("Europe/Riga", "Europe/Riga"),
                            ("Europe/Rome", "Europe/Rome"),
                            ("Europe/Samara", "Europe/Samara"),
                            ("Europe/San_Marino", "Europe/San_Marino"),
                            ("Europe/Sarajevo", "Europe/Sarajevo"),
                            ("Europe/Simferopol", "Europe/Simferopol"),
                            ("Europe/Skopje", "Europe/Skopje"),
                            ("Europe/Sofia", "Europe/Sofia"),
                            ("Europe/Stockholm", "Europe/Stockholm"),
                            ("Europe/Tallinn", "Europe/Tallinn"),
                            ("Europe/Tirane", "Europe/Tirane"),
                            ("Europe/Uzhgorod", "Europe/Uzhgorod"),
                            ("Europe/Vaduz", "Europe/Vaduz"),
                            ("Europe/Vatican", "Europe/Vatican"),
                            ("Europe/Vienna", "Europe/Vienna"),
                            ("Europe/Vilnius", "Europe/Vilnius"),
                            ("Europe/Volgograd", "Europe/Volgograd"),
                            ("Europe/Warsaw", "Europe/Warsaw"),
                            ("Europe/Zagreb", "Europe/Zagreb"),
                            ("Europe/Zaporozhye", "Europe/Zaporozhye"),
                            ("Europe/Zurich", "Europe/Zurich"),
                            ("GMT", "GMT"),
                            ("Indian/Antananarivo", "Indian/Antananarivo"),
                            ("Indian/Chagos", "Indian/Chagos"),
                            ("Indian/Christmas", "Indian/Christmas"),
                            ("Indian/Cocos", "Indian/Cocos"),
                            ("Indian/Comoro", "Indian/Comoro"),
                            ("Indian/Kerguelen", "Indian/Kerguelen"),
                            ("Indian/Mahe", "Indian/Mahe"),
                            ("Indian/Maldives", "Indian/Maldives"),
                            ("Indian/Mauritius", "Indian/Mauritius"),
                            ("Indian/Mayotte", "Indian/Mayotte"),
                            ("Indian/Reunion", "Indian/Reunion"),
                            ("Pacific/Apia", "Pacific/Apia"),
                            ("Pacific/Auckland", "Pacific/Auckland"),
                            ("Pacific/Chatham", "Pacific/Chatham"),
                            ("Pacific/Chuuk", "Pacific/Chuuk"),
                            ("Pacific/Easter", "Pacific/Easter"),
                            ("Pacific/Efate", "Pacific/Efate"),
                            ("Pacific/Enderbury", "Pacific/Enderbury"),
                            ("Pacific/Fakaofo", "Pacific/Fakaofo"),
                            ("Pacific/Fiji", "Pacific/Fiji"),
                            ("Pacific/Funafuti", "Pacific/Funafuti"),
                            ("Pacific/Galapagos", "Pacific/Galapagos"),
                            ("Pacific/Gambier", "Pacific/Gambier"),
                            ("Pacific/Guadalcanal", "Pacific/Guadalcanal"),
                            ("Pacific/Guam", "Pacific/Guam"),
                            ("Pacific/Honolulu", "Pacific/Honolulu"),
                            ("Pacific/Johnston", "Pacific/Johnston"),
                            ("Pacific/Kiritimati", "Pacific/Kiritimati"),
                            ("Pacific/Kosrae", "Pacific/Kosrae"),
                            ("Pacific/Kwajalein", "Pacific/Kwajalein"),
                            ("Pacific/Majuro", "Pacific/Majuro"),
                            ("Pacific/Marquesas", "Pacific/Marquesas"),
                            ("Pacific/Midway", "Pacific/Midway"),
                            ("Pacific/Nauru", "Pacific/Nauru"),
                            ("Pacific/Niue", "Pacific/Niue"),
                            ("Pacific/Norfolk", "Pacific/Norfolk"),
                            ("Pacific/Noumea", "Pacific/Noumea"),
                            ("Pacific/Pago_Pago", "Pacific/Pago_Pago"),
                            ("Pacific/Palau", "Pacific/Palau"),
                            ("Pacific/Pitcairn", "Pacific/Pitcairn"),
                            ("Pacific/Pohnpei", "Pacific/Pohnpei"),
                            ("Pacific/Port_Moresby", "Pacific/Port_Moresby"),
                            ("Pacific/Rarotonga", "Pacific/Rarotonga"),
                            ("Pacific/Saipan", "Pacific/Saipan"),
                            ("Pacific/Tahiti", "Pacific/Tahiti"),
                            ("Pacific/Tarawa", "Pacific/Tarawa"),
                            ("Pacific/Tongatapu", "Pacific/Tongatapu"),
                            ("Pacific/Wake", "Pacific/Wake"),
                            ("Pacific/Wallis", "Pacific/Wallis"),
                            ("US/Alaska", "US/Alaska"),
                            ("US/Arizona", "US/Arizona"),
                            ("US/Central", "US/Central"),
                            ("US/Eastern", "US/Eastern"),
                            ("US/Hawaii", "US/Hawaii"),
                            ("US/Mountain", "US/Mountain"),
                            ("US/Pacific", "US/Pacific"),
                            ("UTC", "UTC"),
                        ],
                    ),
                ),
                (
                    "check_for_updates",
                    models.BooleanField(
                        default=True,
                        help_text='Periodically check for updates (<a href="https://kegbot.org/about/checkin">more info</a>)',
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="KegTap",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text='The display name for this tap, for example, "Main Tap".',
                        max_length=128,
                    ),
                ),
                (
                    "description",
                    models.TextField(
                        help_text="User-visible description for this tap.", null=True, blank=True
                    ),
                ),
                (
                    "sort_order",
                    models.PositiveIntegerField(
                        default=0,
                        help_text="Position relative to other taps when sorting (0=first).",
                    ),
                ),
                (
                    "current_keg",
                    models.OneToOneField(
                        related_name="current_tap",
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="core.Keg",
                        help_text="Keg currently connected to this tap.",
                    ),
                ),
            ],
            options={
                "ordering": ("sort_order", "id"),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="NotificationSettings",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "backend",
                    models.CharField(
                        help_text="Notification backend (dotted path) for these settings.",
                        max_length=255,
                    ),
                ),
                (
                    "keg_tapped",
                    models.BooleanField(default=True, help_text="Sent when a keg is activated."),
                ),
                (
                    "session_started",
                    models.BooleanField(
                        default=False, help_text="Sent when a new drinking session starts."
                    ),
                ),
                (
                    "keg_volume_low",
                    models.BooleanField(default=False, help_text="Sent when a keg becomes low."),
                ),
                (
                    "keg_ended",
                    models.BooleanField(
                        default=False, help_text="Sent when a keg has been taken offline."
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        help_text="User for these settings.",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Picture",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "image",
                    models.ImageField(
                        help_text="The image", upload_to=pykeg.core.models._pics_file_name
                    ),
                ),
                (
                    "time",
                    models.DateTimeField(
                        default=django.utils.timezone.now, help_text="Time/date of image capture"
                    ),
                ),
                (
                    "caption",
                    models.TextField(
                        help_text="Caption for the picture, if any.", null=True, blank=True
                    ),
                ),
                (
                    "keg",
                    models.ForeignKey(
                        related_name="pictures",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="core.Keg",
                        help_text="Keg this picture was taken with, if any.",
                        null=True,
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        related_name="pictures",
                        on_delete=django.db.models.deletion.SET_NULL,
                        blank=True,
                        to="core.DrinkingSession",
                        help_text="Session this picture was taken with, if any.",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="pictures",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        help_text="User that owns/uploaded this picture",
                        null=True,
                    ),
                ),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="PluginData",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("plugin_name", models.CharField(help_text="Plugin short name", max_length=127)),
                ("key", models.CharField(max_length=127)),
                ("value", pykeg.core.jsonfield.JSONField()),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Stats",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("time", models.DateTimeField(default=django.utils.timezone.now)),
                ("stats", pykeg.core.jsonfield.JSONField()),
                (
                    "is_first",
                    models.BooleanField(
                        default=False,
                        help_text="True if this is the most first record for the view.",
                    ),
                ),
                (
                    "drink",
                    models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to="core.Drink"),
                ),
                (
                    "keg",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stats",
                        to="core.Keg",
                        null=True,
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stats",
                        to="core.DrinkingSession",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="stats",
                        to=settings.AUTH_USER_MODEL,
                        null=True,
                    ),
                ),
            ],
            options={
                "get_latest_by": "id",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="SystemEvent",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                (
                    "kind",
                    models.CharField(
                        help_text="Type of event.",
                        max_length=255,
                        choices=[
                            ("drink_poured", "Drink poured"),
                            ("session_started", "Session started"),
                            ("session_joined", "User joined session"),
                            ("keg_tapped", "Keg tapped"),
                            ("keg_volume_low", "Keg volume low"),
                            ("keg_ended", "Keg ended"),
                        ],
                    ),
                ),
                ("time", models.DateTimeField(help_text="Time of the event.")),
                (
                    "drink",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        blank=True,
                        to="core.Drink",
                        help_text="Drink involved in the event, if any.",
                        null=True,
                    ),
                ),
                (
                    "keg",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        blank=True,
                        to="core.Keg",
                        help_text="Keg involved in the event, if any.",
                        null=True,
                    ),
                ),
                (
                    "session",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        blank=True,
                        to="core.DrinkingSession",
                        help_text="Session involved in the event, if any.",
                        null=True,
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="events",
                        blank=True,
                        to=settings.AUTH_USER_MODEL,
                        help_text="User responsible for the event, if any.",
                        null=True,
                    ),
                ),
            ],
            options={
                "ordering": ("-id",),
                "get_latest_by": "time",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="Thermolog",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("temp", models.FloatField()),
                ("time", models.DateTimeField()),
            ],
            options={
                "ordering": ("-time",),
                "get_latest_by": "time",
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name="ThermoSensor",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID", serialize=False, auto_created=True, primary_key=True
                    ),
                ),
                ("raw_name", models.CharField(max_length=256)),
                ("nice_name", models.CharField(max_length=128)),
            ],
            options={},
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name="thermolog",
            name="sensor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="core.ThermoSensor"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="stats",
            unique_together=set([("drink", "user", "keg", "session")]),
        ),
        migrations.AlterUniqueTogether(
            name="plugindata",
            unique_together=set([("plugin_name", "key")]),
        ),
        migrations.AlterUniqueTogether(
            name="notificationsettings",
            unique_together=set([("user", "backend")]),
        ),
        migrations.AddField(
            model_name="kegtap",
            name="temperature_sensor",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="core.ThermoSensor",
                help_text="Optional sensor monitoring the temperature at this tap.",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="kegbotsite",
            name="background_image",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="core.Picture",
                help_text="Background for this site.",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="flowtoggle",
            name="tap",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="toggle",
                null=True,
                blank=True,
                to="core.KegTap",
                help_text="Tap to which this toggle is currently bound.",
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="flowtoggle",
            unique_together=set([("controller", "port_name")]),
        ),
        migrations.AddField(
            model_name="flowmeter",
            name="tap",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="meter",
                null=True,
                blank=True,
                to="core.KegTap",
                help_text="Tap to which this meter is currently bound.",
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="flowmeter",
            unique_together=set([("controller", "port_name")]),
        ),
        migrations.AddField(
            model_name="drink",
            name="keg",
            field=models.ForeignKey(
                related_name="drinks",
                on_delete=django.db.models.deletion.PROTECT,
                editable=False,
                to="core.Keg",
                help_text="Keg against which this Drink is accounted.",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="drink",
            name="picture",
            field=models.OneToOneField(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="core.Picture",
                help_text="Picture snapped with this drink.",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="drink",
            name="session",
            field=models.ForeignKey(
                related_name="drinks",
                on_delete=django.db.models.deletion.PROTECT,
                blank=True,
                editable=False,
                to="core.DrinkingSession",
                help_text="Session where this Drink is grouped.",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="drink",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="drinks",
                editable=False,
                to=settings.AUTH_USER_MODEL,
                help_text="User responsible for this Drink, or None if anonymous/unknown.",
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="beverageproducer",
            name="picture",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="core.Picture",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="beverage",
            name="picture",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="core.Picture",
                help_text="Label image.",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="beverage",
            name="producer",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT, to="core.BeverageProducer"
            ),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name="authenticationtoken",
            unique_together=set([("auth_device", "token_value")]),
        ),
        migrations.AddField(
            model_name="apikey",
            name="device",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.SET_NULL,
                to="core.Device",
                help_text="Device this key is associated with.",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="apikey",
            name="user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                blank=True,
                to=settings.AUTH_USER_MODEL,
                help_text="User receiving API access.",
                null=True,
            ),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name="user",
            name="mugshot",
            field=models.ForeignKey(
                related_name="user_mugshot",
                on_delete=django.db.models.deletion.SET_NULL,
                blank=True,
                to="core.Picture",
                null=True,
            ),
            preserve_default=True,
        ),
    ]
