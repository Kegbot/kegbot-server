# -*- coding: utf-8 -*-
from __future__ import unicode_literals

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

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, numbers and @/./+/-/_ characters', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator(re.compile(b'^[\\w.@+-]+$'), 'Enter a valid username.', b'invalid')])),
                ('display_name', models.CharField(default=b'', help_text=b'Full name, will be shown in some places instead of username', max_length=127)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('activation_key', models.CharField(help_text=b'Unguessable token, used to finish registration.', max_length=128, null=True, blank=True)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ApiKey',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('key', models.CharField(default=pykeg.core.models.get_default_api_key, help_text=b'The secret key.', unique=True, max_length=127, editable=False)),
                ('active', models.BooleanField(default=True, help_text=b'Whether access by this key is currently allowed.')),
                ('description', models.TextField(help_text=b'Information about this key.', null=True, blank=True)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time the key was created.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AuthenticationToken',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('auth_device', models.CharField(help_text=b'Namespace for this token.', max_length=64)),
                ('token_value', models.CharField(help_text=b'Actual value of the token, unique within an auth_device.', max_length=128)),
                ('nice_name', models.CharField(help_text=b'A human-readable alias for the token, for example "Guest Key".', max_length=256, null=True, blank=True)),
                ('pin', models.CharField(help_text=b'A secret value necessary to authenticate with this token.', max_length=256, null=True, blank=True)),
                ('enabled', models.BooleanField(default=True, help_text=b'Whether this token is considered active.')),
                ('created_time', models.DateTimeField(help_text=b'Date token was first added to the system.', auto_now_add=True)),
                ('expire_time', models.DateTimeField(help_text=b'Date after which token is treated as disabled.', null=True, blank=True)),
                ('user', models.ForeignKey(related_name='tokens', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'User in possession of and authenticated by this token.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Beverage',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Name of the beverage, such as "Potrero Pale".', max_length=255)),
                ('beverage_type', models.CharField(default=b'beer', max_length=32, choices=[(b'beer', b'Beer'), (b'wine', b'Wine'), (b'soda', b'Soda'), (b'kombucha', b'Kombucha'), (b'other', b'Other/Unknown')])),
                ('style', models.CharField(help_text=b'Beverage style within type, eg "Pale Ale", "Pinot Noir".', max_length=255, null=True, blank=True)),
                ('description', models.TextField(help_text=b'Free-form description of the beverage.', null=True, blank=True)),
                ('vintage_year', models.DateField(help_text=b'Date of production, for wines or special/seasonal editions', null=True, blank=True)),
                ('abv_percent', models.FloatField(help_text=b'Alcohol by volume, as percentage (0.0-100.0).', null=True, verbose_name=b'ABV Percentage', blank=True)),
                ('calories_per_ml', models.FloatField(help_text=b'Calories per mL of beverage.', null=True, blank=True)),
                ('carbs_per_ml', models.FloatField(help_text=b'Carbohydrates per mL of beverage.', null=True, blank=True)),
                ('color_hex', models.CharField(default=b'#C35900', help_text=b'Approximate beverage color', max_length=16, verbose_name=b'Color (Hex Value)', validators=[django.core.validators.RegexValidator(regex=b'(^#[0-9a-zA-Z]{3}$)|(^#[0-9a-zA-Z]{6}$)', message=b'Color must start with "#" and include 3 or 6 hex characters, like #123 or #123456.', code=b'bad_color')])),
                ('original_gravity', models.FloatField(help_text=b'Original gravity (beer only).', null=True, blank=True)),
                ('specific_gravity', models.FloatField(help_text=b'Final gravity (beer only).', null=True, blank=True)),
                ('srm', models.FloatField(help_text=b'Standard Reference Method value (beer only).', null=True, verbose_name=b'SRM Value', blank=True)),
                ('ibu', models.FloatField(help_text=b'International Bittering Units value (beer only).', null=True, verbose_name=b'IBUs', blank=True)),
                ('star_rating', models.FloatField(blank=True, help_text=b'Star rating for beverage (0: worst, 5: best)', null=True, validators=[django.core.validators.MinValueValidator(0.0), django.core.validators.MaxValueValidator(5.0)])),
                ('untappd_beer_id', models.IntegerField(help_text=b'Untappd.com resource ID (beer only).', null=True, blank=True)),
                ('beverage_backend', models.CharField(help_text=b'Future use.', max_length=255, null=True, blank=True)),
                ('beverage_backend_id', models.CharField(help_text=b'Future use.', max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='BeverageProducer',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Name of the brewer', max_length=255)),
                ('country', pykeg.core.fields.CountryField(default=b'USA', help_text=b'Country of origin', max_length=3, choices=[(b'AFG', 'Afghanistan'), (b'ALA', 'Aland Islands'), (b'ALB', 'Albania'), (b'DZA', 'Algeria'), (b'ASM', 'American Samoa'), (b'AND', 'Andorra'), (b'AGO', 'Angola'), (b'AIA', 'Anguilla'), (b'ATG', 'Antigua and Barbuda'), (b'ARG', 'Argentina'), (b'ARM', 'Armenia'), (b'ABW', 'Aruba'), (b'AUS', 'Australia'), (b'AUT', 'Austria'), (b'AZE', 'Azerbaijan'), (b'BHS', 'Bahamas'), (b'BHR', 'Bahrain'), (b'BGD', 'Bangladesh'), (b'BRB', 'Barbados'), (b'BLR', 'Belarus'), (b'BEL', 'Belgium'), (b'BLZ', 'Belize'), (b'BEN', 'Benin'), (b'BMU', 'Bermuda'), (b'BTN', 'Bhutan'), (b'BOL', 'Bolivia'), (b'BIH', 'Bosnia and Herzegovina'), (b'BWA', 'Botswana'), (b'BRA', 'Brazil'), (b'VGB', 'British Virgin Islands'), (b'BRN', 'Brunei Darussalam'), (b'BGR', 'Bulgaria'), (b'BFA', 'Burkina Faso'), (b'BDI', 'Burundi'), (b'KHM', 'Cambodia'), (b'CMR', 'Cameroon'), (b'CAN', 'Canada'), (b'CPV', 'Cape Verde'), (b'CYM', 'Cayman Islands'), (b'CAF', 'Central African Republic'), (b'TCD', 'Chad'), (b'CIL', 'Channel Islands'), (b'CHL', 'Chile'), (b'CHN', 'China'), (b'HKG', 'China - Hong Kong'), (b'MAC', 'China - Macao'), (b'COL', 'Colombia'), (b'COM', 'Comoros'), (b'COG', 'Congo'), (b'COK', 'Cook Islands'), (b'CRI', 'Costa Rica'), (b'CIV', "Cote d'Ivoire"), (b'HRV', 'Croatia'), (b'CUB', 'Cuba'), (b'CYP', 'Cyprus'), (b'CZE', 'Czech Republic'), (b'PRK', "Democratic People's Republic of Korea"), (b'COD', 'Democratic Republic of the Congo'), (b'DNK', 'Denmark'), (b'DJI', 'Djibouti'), (b'DMA', 'Dominica'), (b'DOM', 'Dominican Republic'), (b'ECU', 'Ecuador'), (b'EGY', 'Egypt'), (b'SLV', 'El Salvador'), (b'GNQ', 'Equatorial Guinea'), (b'ERI', 'Eritrea'), (b'EST', 'Estonia'), (b'ETH', 'Ethiopia'), (b'FRO', 'Faeroe Islands'), (b'FLK', 'Falkland Islands (Malvinas)'), (b'FJI', 'Fiji'), (b'FIN', 'Finland'), (b'FRA', 'France'), (b'GUF', 'French Guiana'), (b'PYF', 'French Polynesia'), (b'GAB', 'Gabon'), (b'GMB', 'Gambia'), (b'GEO', 'Georgia'), (b'DEU', 'Germany'), (b'GHA', 'Ghana'), (b'GIB', 'Gibraltar'), (b'GRC', 'Greece'), (b'GRL', 'Greenland'), (b'GRD', 'Grenada'), (b'GLP', 'Guadeloupe'), (b'GUM', 'Guam'), (b'GTM', 'Guatemala'), (b'GGY', 'Guernsey'), (b'GIN', 'Guinea'), (b'GNB', 'Guinea-Bissau'), (b'GUY', 'Guyana'), (b'HTI', 'Haiti'), (b'VAT', 'Holy See (Vatican City)'), (b'HND', 'Honduras'), (b'HUN', 'Hungary'), (b'ISL', 'Iceland'), (b'IND', 'India'), (b'IDN', 'Indonesia'), (b'IRN', 'Iran'), (b'IRQ', 'Iraq'), (b'IRL', 'Ireland'), (b'IMN', 'Isle of Man'), (b'ISR', 'Israel'), (b'ITA', 'Italy'), (b'JAM', 'Jamaica'), (b'JPN', 'Japan'), (b'JEY', 'Jersey'), (b'JOR', 'Jordan'), (b'KAZ', 'Kazakhstan'), (b'KEN', 'Kenya'), (b'KIR', 'Kiribati'), (b'KWT', 'Kuwait'), (b'KGZ', 'Kyrgyzstan'), (b'LAO', "Lao People's Democratic Republic"), (b'LVA', 'Latvia'), (b'LBN', 'Lebanon'), (b'LSO', 'Lesotho'), (b'LBR', 'Liberia'), (b'LBY', 'Libyan Arab Jamahiriya'), (b'LIE', 'Liechtenstein'), (b'LTU', 'Lithuania'), (b'LUX', 'Luxembourg'), (b'MKD', 'Macedonia'), (b'MDG', 'Madagascar'), (b'MWI', 'Malawi'), (b'MYS', 'Malaysia'), (b'MDV', 'Maldives'), (b'MLI', 'Mali'), (b'MLT', 'Malta'), (b'MHL', 'Marshall Islands'), (b'MTQ', 'Martinique'), (b'MRT', 'Mauritania'), (b'MUS', 'Mauritius'), (b'MYT', 'Mayotte'), (b'MEX', 'Mexico'), (b'FSM', 'Micronesia, Federated States of'), (b'MCO', 'Monaco'), (b'MNG', 'Mongolia'), (b'MNE', 'Montenegro'), (b'MSR', 'Montserrat'), (b'MAR', 'Morocco'), (b'MOZ', 'Mozambique'), (b'MMR', 'Myanmar'), (b'NAM', 'Namibia'), (b'NRU', 'Nauru'), (b'NPL', 'Nepal'), (b'NLD', 'Netherlands'), (b'ANT', 'Netherlands Antilles'), (b'NCL', 'New Caledonia'), (b'NZL', 'New Zealand'), (b'NIC', 'Nicaragua'), (b'NER', 'Niger'), (b'NGA', 'Nigeria'), (b'NIU', 'Niue'), (b'NFK', 'Norfolk Island'), (b'MNP', 'Northern Mariana Islands'), (b'NOR', 'Norway'), (b'PSE', 'Occupied Palestinian Territory'), (b'OMN', 'Oman'), (b'PAK', 'Pakistan'), (b'PLW', 'Palau'), (b'PAN', 'Panama'), (b'PNG', 'Papua New Guinea'), (b'PRY', 'Paraguay'), (b'PER', 'Peru'), (b'PHL', 'Philippines'), (b'PCN', 'Pitcairn'), (b'POL', 'Poland'), (b'PRT', 'Portugal'), (b'PRI', 'Puerto Rico'), (b'QAT', 'Qatar'), (b'KOR', 'Republic of Korea'), (b'MDA', 'Republic of Moldova'), (b'REU', 'Reunion'), (b'ROU', 'Romania'), (b'RUS', 'Russian Federation'), (b'RWA', 'Rwanda'), (b'BLM', 'Saint-Barthelemy'), (b'SHN', 'Saint Helena'), (b'KNA', 'Saint Kitts and Nevis'), (b'LCA', 'Saint Lucia'), (b'MAF', 'Saint-Martin (French part)'), (b'SPM', 'Saint Pierre and Miquelon'), (b'VCT', 'Saint Vincent and the Grenadines'), (b'WSM', 'Samoa'), (b'SMR', 'San Marino'), (b'STP', 'Sao Tome and Principe'), (b'SAU', 'Saudi Arabia'), (b'SEN', 'Senegal'), (b'SRB', 'Serbia'), (b'SYC', 'Seychelles'), (b'SLE', 'Sierra Leone'), (b'SGP', 'Singapore'), (b'SVK', 'Slovakia'), (b'SVN', 'Slovenia'), (b'SLB', 'Solomon Islands'), (b'SOM', 'Somalia'), (b'ZAF', 'South Africa'), (b'ESP', 'Spain'), (b'LKA', 'Sri Lanka'), (b'SDN', 'Sudan'), (b'SUR', 'Suriname'), (b'SJM', 'Svalbard and Jan Mayen Islands'), (b'SWZ', 'Swaziland'), (b'SWE', 'Sweden'), (b'CHE', 'Switzerland'), (b'SYR', 'Syrian Arab Republic'), (b'TJK', 'Tajikistan'), (b'THA', 'Thailand'), (b'TLS', 'Timor-Leste'), (b'TGO', 'Togo'), (b'TKL', 'Tokelau'), (b'TON', 'Tonga'), (b'TTO', 'Trinidad and Tobago'), (b'TUN', 'Tunisia'), (b'TUR', 'Turkey'), (b'TKM', 'Turkmenistan'), (b'TCA', 'Turks and Caicos Islands'), (b'TUV', 'Tuvalu'), (b'UGA', 'Uganda'), (b'UKR', 'Ukraine'), (b'ARE', 'United Arab Emirates'), (b'GBR', 'United Kingdom'), (b'TZA', 'United Republic of Tanzania'), (b'USA', 'United States of America'), (b'VIR', 'United States Virgin Islands'), (b'URY', 'Uruguay'), (b'UZB', 'Uzbekistan'), (b'VUT', 'Vanuatu'), (b'VEN', 'Venezuela (Bolivarian Republic of)'), (b'VNM', 'Viet Nam'), (b'WLF', 'Wallis and Futuna Islands'), (b'ESH', 'Western Sahara'), (b'YEM', 'Yemen'), (b'ZMB', 'Zambia'), (b'ZWE', 'Zimbabwe')])),
                ('origin_state', models.CharField(default=b'', max_length=128, null=True, help_text=b'State of origin, if applicable', blank=True)),
                ('origin_city', models.CharField(default=b'', max_length=128, null=True, help_text=b'City of origin, if known', blank=True)),
                ('is_homebrew', models.BooleanField(default=False)),
                ('url', models.URLField(default=b'', null=True, help_text=b"Brewer's home page", blank=True)),
                ('description', models.TextField(default=b'', help_text=b'A short description of the brewer', null=True, blank=True)),
                ('beverage_backend', models.CharField(help_text=b'Future use.', max_length=255, null=True, blank=True)),
                ('beverage_backend_id', models.CharField(help_text=b'Future use.', max_length=255, null=True, blank=True)),
            ],
            options={
                'ordering': ('name',),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Controller',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'Identifying name for this device; must be unique.', unique=True, max_length=128)),
                ('model_name', models.CharField(help_text=b'Type of controller (optional).', max_length=128, null=True, blank=True)),
                ('serial_number', models.CharField(help_text=b'Serial number (optional).', max_length=128, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Device',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'Unknown Device', max_length=255)),
                ('created_time', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time the device was created.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Drink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ticks', models.PositiveIntegerField(help_text=b'Flow sensor ticks, never changed once recorded.', editable=False)),
                ('volume_ml', models.FloatField(help_text=b'Calculated (or set) Drink volume.', editable=False)),
                ('time', models.DateTimeField(help_text=b'Date and time of pour.', editable=False)),
                ('duration', models.PositiveIntegerField(default=0, help_text=b'Time in seconds taken to pour this Drink.', editable=False, blank=True)),
                ('shout', models.TextField(help_text=b'Comment from the drinker at the time of the pour.', null=True, blank=True)),
                ('tick_time_series', models.TextField(help_text=b'Tick update sequence that generated this drink (diagnostic data).', null=True, editable=False, blank=True)),
            ],
            options={
                'ordering': ('-time',),
                'get_latest_by': 'time',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DrinkingSession',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_time', models.DateTimeField()),
                ('end_time', models.DateTimeField()),
                ('volume_ml', models.FloatField(default=0)),
                ('name', models.CharField(max_length=256, null=True, blank=True)),
            ],
            options={
                'ordering': ('-start_time',),
                'get_latest_by': 'start_time',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowMeter',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('port_name', models.CharField(help_text=b'Controller-specific data port name for this meter.', max_length=128)),
                ('ticks_per_ml', models.FloatField(default=2.724, help_text=b'Flow meter pulses per mL of fluid.  Common values: 2.724 (FT330-RJ), 5.4 (SF800)')),
                ('controller', models.ForeignKey(related_name='meters', to='core.Controller', help_text=b'Controller that owns this meter.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FlowToggle',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('port_name', models.CharField(help_text=b'Controller-specific data port name for this toggle.', max_length=128)),
                ('controller', models.ForeignKey(related_name='toggles', to='core.Controller', help_text=b'Controller that owns this toggle.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('invite_code', models.CharField(default=pykeg.core.models.get_default_invite_code, help_text=b'Unguessable token which must be presented to use this invite', unique=True, max_length=255)),
                ('for_email', models.EmailField(help_text=b'Address this invitation was sent to.', max_length=75)),
                ('invited_date', models.DateTimeField(help_text=b'Date and time the invitation was sent', verbose_name='date invited', auto_now_add=True)),
                ('expires_date', models.DateTimeField(default=pykeg.core.models.get_default_expires_date, help_text=b'Date and time after which the invitation is considered expired', verbose_name='date expries')),
                ('invited_by', models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, help_text=b'User that created this invitation, if any.', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Keg',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('keg_type', models.CharField(default=b'half-barrel', help_text=b"Keg container type, used to initialize keg's full volume", max_length=32, choices=[(b'quarter', b'Quarter Barrel (7.75 gal)'), (b'corny', b'Corny Keg (5 gal)'), (b'sixth', b'Sixth Barrel (5.17 gal)'), (b'other', b'Other'), (b'euro-half', b'European Half Barrel (50 L)'), (b'half-barrel', b'Half Barrel (15.5 gal)'), (b'euro', b'European Full Barrel (100 L)')])),
                ('served_volume_ml', models.FloatField(default=0, help_text=b'Computed served volume.', editable=False)),
                ('full_volume_ml', models.FloatField(default=0, help_text=b'Full volume of this Keg; usually set automatically from keg_type.', editable=False)),
                ('start_time', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time the Keg was first tapped.')),
                ('end_time', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time the Keg was finished or disconnected.')),
                ('online', models.BooleanField(default=True, help_text=b'True if the keg is currently assigned to a tap.', editable=False)),
                ('finished', models.BooleanField(default=False, help_text=b'True when the Keg has been exhausted or discarded.', editable=False)),
                ('description', models.CharField(help_text=b'User-visible description of the Keg.', max_length=256, null=True, blank=True)),
                ('spilled_ml', models.FloatField(default=0, help_text=b'Amount of beverage poured without an associated Drink.')),
                ('notes', models.TextField(help_text=b'Private notes about this keg, viewable only by admins.', null=True, blank=True)),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Beverage', help_text=b'Beverage in this Keg.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KegbotSite',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(default=b'default', unique=True, max_length=64, editable=False)),
                ('server_version', models.CharField(max_length=64, null=True, editable=False)),
                ('is_setup', models.BooleanField(default=False, help_text=b'True if the site has completed setup.', editable=False)),
                ('registration_id', models.TextField(default=b'', help_text=b'A unique id for this system.', max_length=128, editable=False, blank=True)),
                ('volume_display_units', models.CharField(default=b'imperial', help_text=b'Unit system to use when displaying volumetric data.', max_length=64, choices=[(b'metric', b'Metric (mL, L)'), (b'imperial', b'Imperial (oz, pint)')])),
                ('temperature_display_units', models.CharField(default=b'f', help_text=b'Unit system to use when displaying temperature data.', max_length=64, choices=[(b'f', b'Fahrenheit'), (b'c', b'Celsius')])),
                ('title', models.CharField(default=b'My Kegbot', help_text=b'The title of this site.', max_length=64)),
                ('google_analytics_id', models.CharField(help_text=b'Set to your Google Analytics ID to enable tracking. Example: UA-XXXX-y', max_length=64, null=True, blank=True)),
                ('session_timeout_minutes', models.PositiveIntegerField(default=180, help_text=b'Maximum time, in minutes, that a session may be idle (no pours) before it is considered to be finished.  Recommended value is 180.')),
                ('privacy', models.CharField(default=b'public', help_text=b'Who can view Kegbot data?', max_length=63, choices=[(b'public', b'Public: Browsing does not require login'), (b'members', b'Members only: Must log in to browse'), (b'staff', b'Staff only: Only logged-in staff accounts may browse')])),
                ('registration_mode', models.CharField(default=b'public', help_text=b'Who can join this Kegbot from the web site?', max_length=63, choices=[(b'public', b'Public: Anyone can register.'), (b'member-invite-only', b'Member Invite: Must be invited by an existing member.'), (b'staff-invite-only', b'Staff Invite Only: Must be invited by a staff member.')])),
                ('timezone', models.CharField(default=b'UTC', help_text=b'Time zone for this system.', max_length=255, choices=[(b'Africa/Abidjan', b'Africa/Abidjan'), (b'Africa/Accra', b'Africa/Accra'), (b'Africa/Addis_Ababa', b'Africa/Addis_Ababa'), (b'Africa/Algiers', b'Africa/Algiers'), (b'Africa/Asmara', b'Africa/Asmara'), (b'Africa/Bamako', b'Africa/Bamako'), (b'Africa/Bangui', b'Africa/Bangui'), (b'Africa/Banjul', b'Africa/Banjul'), (b'Africa/Bissau', b'Africa/Bissau'), (b'Africa/Blantyre', b'Africa/Blantyre'), (b'Africa/Brazzaville', b'Africa/Brazzaville'), (b'Africa/Bujumbura', b'Africa/Bujumbura'), (b'Africa/Cairo', b'Africa/Cairo'), (b'Africa/Casablanca', b'Africa/Casablanca'), (b'Africa/Ceuta', b'Africa/Ceuta'), (b'Africa/Conakry', b'Africa/Conakry'), (b'Africa/Dakar', b'Africa/Dakar'), (b'Africa/Dar_es_Salaam', b'Africa/Dar_es_Salaam'), (b'Africa/Djibouti', b'Africa/Djibouti'), (b'Africa/Douala', b'Africa/Douala'), (b'Africa/El_Aaiun', b'Africa/El_Aaiun'), (b'Africa/Freetown', b'Africa/Freetown'), (b'Africa/Gaborone', b'Africa/Gaborone'), (b'Africa/Harare', b'Africa/Harare'), (b'Africa/Johannesburg', b'Africa/Johannesburg'), (b'Africa/Juba', b'Africa/Juba'), (b'Africa/Kampala', b'Africa/Kampala'), (b'Africa/Khartoum', b'Africa/Khartoum'), (b'Africa/Kigali', b'Africa/Kigali'), (b'Africa/Kinshasa', b'Africa/Kinshasa'), (b'Africa/Lagos', b'Africa/Lagos'), (b'Africa/Libreville', b'Africa/Libreville'), (b'Africa/Lome', b'Africa/Lome'), (b'Africa/Luanda', b'Africa/Luanda'), (b'Africa/Lubumbashi', b'Africa/Lubumbashi'), (b'Africa/Lusaka', b'Africa/Lusaka'), (b'Africa/Malabo', b'Africa/Malabo'), (b'Africa/Maputo', b'Africa/Maputo'), (b'Africa/Maseru', b'Africa/Maseru'), (b'Africa/Mbabane', b'Africa/Mbabane'), (b'Africa/Mogadishu', b'Africa/Mogadishu'), (b'Africa/Monrovia', b'Africa/Monrovia'), (b'Africa/Nairobi', b'Africa/Nairobi'), (b'Africa/Ndjamena', b'Africa/Ndjamena'), (b'Africa/Niamey', b'Africa/Niamey'), (b'Africa/Nouakchott', b'Africa/Nouakchott'), (b'Africa/Ouagadougou', b'Africa/Ouagadougou'), (b'Africa/Porto-Novo', b'Africa/Porto-Novo'), (b'Africa/Sao_Tome', b'Africa/Sao_Tome'), (b'Africa/Tripoli', b'Africa/Tripoli'), (b'Africa/Tunis', b'Africa/Tunis'), (b'Africa/Windhoek', b'Africa/Windhoek'), (b'America/Adak', b'America/Adak'), (b'America/Anchorage', b'America/Anchorage'), (b'America/Anguilla', b'America/Anguilla'), (b'America/Antigua', b'America/Antigua'), (b'America/Araguaina', b'America/Araguaina'), (b'America/Argentina/Buenos_Aires', b'America/Argentina/Buenos_Aires'), (b'America/Argentina/Catamarca', b'America/Argentina/Catamarca'), (b'America/Argentina/Cordoba', b'America/Argentina/Cordoba'), (b'America/Argentina/Jujuy', b'America/Argentina/Jujuy'), (b'America/Argentina/La_Rioja', b'America/Argentina/La_Rioja'), (b'America/Argentina/Mendoza', b'America/Argentina/Mendoza'), (b'America/Argentina/Rio_Gallegos', b'America/Argentina/Rio_Gallegos'), (b'America/Argentina/Salta', b'America/Argentina/Salta'), (b'America/Argentina/San_Juan', b'America/Argentina/San_Juan'), (b'America/Argentina/San_Luis', b'America/Argentina/San_Luis'), (b'America/Argentina/Tucuman', b'America/Argentina/Tucuman'), (b'America/Argentina/Ushuaia', b'America/Argentina/Ushuaia'), (b'America/Aruba', b'America/Aruba'), (b'America/Asuncion', b'America/Asuncion'), (b'America/Atikokan', b'America/Atikokan'), (b'America/Bahia', b'America/Bahia'), (b'America/Bahia_Banderas', b'America/Bahia_Banderas'), (b'America/Barbados', b'America/Barbados'), (b'America/Belem', b'America/Belem'), (b'America/Belize', b'America/Belize'), (b'America/Blanc-Sablon', b'America/Blanc-Sablon'), (b'America/Boa_Vista', b'America/Boa_Vista'), (b'America/Bogota', b'America/Bogota'), (b'America/Boise', b'America/Boise'), (b'America/Cambridge_Bay', b'America/Cambridge_Bay'), (b'America/Campo_Grande', b'America/Campo_Grande'), (b'America/Cancun', b'America/Cancun'), (b'America/Caracas', b'America/Caracas'), (b'America/Cayenne', b'America/Cayenne'), (b'America/Cayman', b'America/Cayman'), (b'America/Chicago', b'America/Chicago'), (b'America/Chihuahua', b'America/Chihuahua'), (b'America/Costa_Rica', b'America/Costa_Rica'), (b'America/Creston', b'America/Creston'), (b'America/Cuiaba', b'America/Cuiaba'), (b'America/Curacao', b'America/Curacao'), (b'America/Danmarkshavn', b'America/Danmarkshavn'), (b'America/Dawson', b'America/Dawson'), (b'America/Dawson_Creek', b'America/Dawson_Creek'), (b'America/Denver', b'America/Denver'), (b'America/Detroit', b'America/Detroit'), (b'America/Dominica', b'America/Dominica'), (b'America/Edmonton', b'America/Edmonton'), (b'America/Eirunepe', b'America/Eirunepe'), (b'America/El_Salvador', b'America/El_Salvador'), (b'America/Fortaleza', b'America/Fortaleza'), (b'America/Glace_Bay', b'America/Glace_Bay'), (b'America/Godthab', b'America/Godthab'), (b'America/Goose_Bay', b'America/Goose_Bay'), (b'America/Grand_Turk', b'America/Grand_Turk'), (b'America/Grenada', b'America/Grenada'), (b'America/Guadeloupe', b'America/Guadeloupe'), (b'America/Guatemala', b'America/Guatemala'), (b'America/Guayaquil', b'America/Guayaquil'), (b'America/Guyana', b'America/Guyana'), (b'America/Halifax', b'America/Halifax'), (b'America/Havana', b'America/Havana'), (b'America/Hermosillo', b'America/Hermosillo'), (b'America/Indiana/Indianapolis', b'America/Indiana/Indianapolis'), (b'America/Indiana/Knox', b'America/Indiana/Knox'), (b'America/Indiana/Marengo', b'America/Indiana/Marengo'), (b'America/Indiana/Petersburg', b'America/Indiana/Petersburg'), (b'America/Indiana/Tell_City', b'America/Indiana/Tell_City'), (b'America/Indiana/Vevay', b'America/Indiana/Vevay'), (b'America/Indiana/Vincennes', b'America/Indiana/Vincennes'), (b'America/Indiana/Winamac', b'America/Indiana/Winamac'), (b'America/Inuvik', b'America/Inuvik'), (b'America/Iqaluit', b'America/Iqaluit'), (b'America/Jamaica', b'America/Jamaica'), (b'America/Juneau', b'America/Juneau'), (b'America/Kentucky/Louisville', b'America/Kentucky/Louisville'), (b'America/Kentucky/Monticello', b'America/Kentucky/Monticello'), (b'America/Kralendijk', b'America/Kralendijk'), (b'America/La_Paz', b'America/La_Paz'), (b'America/Lima', b'America/Lima'), (b'America/Los_Angeles', b'America/Los_Angeles'), (b'America/Lower_Princes', b'America/Lower_Princes'), (b'America/Maceio', b'America/Maceio'), (b'America/Managua', b'America/Managua'), (b'America/Manaus', b'America/Manaus'), (b'America/Marigot', b'America/Marigot'), (b'America/Martinique', b'America/Martinique'), (b'America/Matamoros', b'America/Matamoros'), (b'America/Mazatlan', b'America/Mazatlan'), (b'America/Menominee', b'America/Menominee'), (b'America/Merida', b'America/Merida'), (b'America/Metlakatla', b'America/Metlakatla'), (b'America/Mexico_City', b'America/Mexico_City'), (b'America/Miquelon', b'America/Miquelon'), (b'America/Moncton', b'America/Moncton'), (b'America/Monterrey', b'America/Monterrey'), (b'America/Montevideo', b'America/Montevideo'), (b'America/Montreal', b'America/Montreal'), (b'America/Montserrat', b'America/Montserrat'), (b'America/Nassau', b'America/Nassau'), (b'America/New_York', b'America/New_York'), (b'America/Nipigon', b'America/Nipigon'), (b'America/Nome', b'America/Nome'), (b'America/Noronha', b'America/Noronha'), (b'America/North_Dakota/Beulah', b'America/North_Dakota/Beulah'), (b'America/North_Dakota/Center', b'America/North_Dakota/Center'), (b'America/North_Dakota/New_Salem', b'America/North_Dakota/New_Salem'), (b'America/Ojinaga', b'America/Ojinaga'), (b'America/Panama', b'America/Panama'), (b'America/Pangnirtung', b'America/Pangnirtung'), (b'America/Paramaribo', b'America/Paramaribo'), (b'America/Phoenix', b'America/Phoenix'), (b'America/Port-au-Prince', b'America/Port-au-Prince'), (b'America/Port_of_Spain', b'America/Port_of_Spain'), (b'America/Porto_Velho', b'America/Porto_Velho'), (b'America/Puerto_Rico', b'America/Puerto_Rico'), (b'America/Rainy_River', b'America/Rainy_River'), (b'America/Rankin_Inlet', b'America/Rankin_Inlet'), (b'America/Recife', b'America/Recife'), (b'America/Regina', b'America/Regina'), (b'America/Resolute', b'America/Resolute'), (b'America/Rio_Branco', b'America/Rio_Branco'), (b'America/Santa_Isabel', b'America/Santa_Isabel'), (b'America/Santarem', b'America/Santarem'), (b'America/Santiago', b'America/Santiago'), (b'America/Santo_Domingo', b'America/Santo_Domingo'), (b'America/Sao_Paulo', b'America/Sao_Paulo'), (b'America/Scoresbysund', b'America/Scoresbysund'), (b'America/Sitka', b'America/Sitka'), (b'America/St_Barthelemy', b'America/St_Barthelemy'), (b'America/St_Johns', b'America/St_Johns'), (b'America/St_Kitts', b'America/St_Kitts'), (b'America/St_Lucia', b'America/St_Lucia'), (b'America/St_Thomas', b'America/St_Thomas'), (b'America/St_Vincent', b'America/St_Vincent'), (b'America/Swift_Current', b'America/Swift_Current'), (b'America/Tegucigalpa', b'America/Tegucigalpa'), (b'America/Thule', b'America/Thule'), (b'America/Thunder_Bay', b'America/Thunder_Bay'), (b'America/Tijuana', b'America/Tijuana'), (b'America/Toronto', b'America/Toronto'), (b'America/Tortola', b'America/Tortola'), (b'America/Vancouver', b'America/Vancouver'), (b'America/Whitehorse', b'America/Whitehorse'), (b'America/Winnipeg', b'America/Winnipeg'), (b'America/Yakutat', b'America/Yakutat'), (b'America/Yellowknife', b'America/Yellowknife'), (b'Antarctica/Casey', b'Antarctica/Casey'), (b'Antarctica/Davis', b'Antarctica/Davis'), (b'Antarctica/DumontDUrville', b'Antarctica/DumontDUrville'), (b'Antarctica/Macquarie', b'Antarctica/Macquarie'), (b'Antarctica/Mawson', b'Antarctica/Mawson'), (b'Antarctica/McMurdo', b'Antarctica/McMurdo'), (b'Antarctica/Palmer', b'Antarctica/Palmer'), (b'Antarctica/Rothera', b'Antarctica/Rothera'), (b'Antarctica/Syowa', b'Antarctica/Syowa'), (b'Antarctica/Troll', b'Antarctica/Troll'), (b'Antarctica/Vostok', b'Antarctica/Vostok'), (b'Arctic/Longyearbyen', b'Arctic/Longyearbyen'), (b'Asia/Aden', b'Asia/Aden'), (b'Asia/Almaty', b'Asia/Almaty'), (b'Asia/Amman', b'Asia/Amman'), (b'Asia/Anadyr', b'Asia/Anadyr'), (b'Asia/Aqtau', b'Asia/Aqtau'), (b'Asia/Aqtobe', b'Asia/Aqtobe'), (b'Asia/Ashgabat', b'Asia/Ashgabat'), (b'Asia/Baghdad', b'Asia/Baghdad'), (b'Asia/Bahrain', b'Asia/Bahrain'), (b'Asia/Baku', b'Asia/Baku'), (b'Asia/Bangkok', b'Asia/Bangkok'), (b'Asia/Beirut', b'Asia/Beirut'), (b'Asia/Bishkek', b'Asia/Bishkek'), (b'Asia/Brunei', b'Asia/Brunei'), (b'Asia/Choibalsan', b'Asia/Choibalsan'), (b'Asia/Chongqing', b'Asia/Chongqing'), (b'Asia/Colombo', b'Asia/Colombo'), (b'Asia/Damascus', b'Asia/Damascus'), (b'Asia/Dhaka', b'Asia/Dhaka'), (b'Asia/Dili', b'Asia/Dili'), (b'Asia/Dubai', b'Asia/Dubai'), (b'Asia/Dushanbe', b'Asia/Dushanbe'), (b'Asia/Gaza', b'Asia/Gaza'), (b'Asia/Harbin', b'Asia/Harbin'), (b'Asia/Hebron', b'Asia/Hebron'), (b'Asia/Ho_Chi_Minh', b'Asia/Ho_Chi_Minh'), (b'Asia/Hong_Kong', b'Asia/Hong_Kong'), (b'Asia/Hovd', b'Asia/Hovd'), (b'Asia/Irkutsk', b'Asia/Irkutsk'), (b'Asia/Jakarta', b'Asia/Jakarta'), (b'Asia/Jayapura', b'Asia/Jayapura'), (b'Asia/Jerusalem', b'Asia/Jerusalem'), (b'Asia/Kabul', b'Asia/Kabul'), (b'Asia/Kamchatka', b'Asia/Kamchatka'), (b'Asia/Karachi', b'Asia/Karachi'), (b'Asia/Kashgar', b'Asia/Kashgar'), (b'Asia/Kathmandu', b'Asia/Kathmandu'), (b'Asia/Khandyga', b'Asia/Khandyga'), (b'Asia/Kolkata', b'Asia/Kolkata'), (b'Asia/Krasnoyarsk', b'Asia/Krasnoyarsk'), (b'Asia/Kuala_Lumpur', b'Asia/Kuala_Lumpur'), (b'Asia/Kuching', b'Asia/Kuching'), (b'Asia/Kuwait', b'Asia/Kuwait'), (b'Asia/Macau', b'Asia/Macau'), (b'Asia/Magadan', b'Asia/Magadan'), (b'Asia/Makassar', b'Asia/Makassar'), (b'Asia/Manila', b'Asia/Manila'), (b'Asia/Muscat', b'Asia/Muscat'), (b'Asia/Nicosia', b'Asia/Nicosia'), (b'Asia/Novokuznetsk', b'Asia/Novokuznetsk'), (b'Asia/Novosibirsk', b'Asia/Novosibirsk'), (b'Asia/Omsk', b'Asia/Omsk'), (b'Asia/Oral', b'Asia/Oral'), (b'Asia/Phnom_Penh', b'Asia/Phnom_Penh'), (b'Asia/Pontianak', b'Asia/Pontianak'), (b'Asia/Pyongyang', b'Asia/Pyongyang'), (b'Asia/Qatar', b'Asia/Qatar'), (b'Asia/Qyzylorda', b'Asia/Qyzylorda'), (b'Asia/Rangoon', b'Asia/Rangoon'), (b'Asia/Riyadh', b'Asia/Riyadh'), (b'Asia/Sakhalin', b'Asia/Sakhalin'), (b'Asia/Samarkand', b'Asia/Samarkand'), (b'Asia/Seoul', b'Asia/Seoul'), (b'Asia/Shanghai', b'Asia/Shanghai'), (b'Asia/Singapore', b'Asia/Singapore'), (b'Asia/Taipei', b'Asia/Taipei'), (b'Asia/Tashkent', b'Asia/Tashkent'), (b'Asia/Tbilisi', b'Asia/Tbilisi'), (b'Asia/Tehran', b'Asia/Tehran'), (b'Asia/Thimphu', b'Asia/Thimphu'), (b'Asia/Tokyo', b'Asia/Tokyo'), (b'Asia/Ulaanbaatar', b'Asia/Ulaanbaatar'), (b'Asia/Urumqi', b'Asia/Urumqi'), (b'Asia/Ust-Nera', b'Asia/Ust-Nera'), (b'Asia/Vientiane', b'Asia/Vientiane'), (b'Asia/Vladivostok', b'Asia/Vladivostok'), (b'Asia/Yakutsk', b'Asia/Yakutsk'), (b'Asia/Yekaterinburg', b'Asia/Yekaterinburg'), (b'Asia/Yerevan', b'Asia/Yerevan'), (b'Atlantic/Azores', b'Atlantic/Azores'), (b'Atlantic/Bermuda', b'Atlantic/Bermuda'), (b'Atlantic/Canary', b'Atlantic/Canary'), (b'Atlantic/Cape_Verde', b'Atlantic/Cape_Verde'), (b'Atlantic/Faroe', b'Atlantic/Faroe'), (b'Atlantic/Madeira', b'Atlantic/Madeira'), (b'Atlantic/Reykjavik', b'Atlantic/Reykjavik'), (b'Atlantic/South_Georgia', b'Atlantic/South_Georgia'), (b'Atlantic/St_Helena', b'Atlantic/St_Helena'), (b'Atlantic/Stanley', b'Atlantic/Stanley'), (b'Australia/Adelaide', b'Australia/Adelaide'), (b'Australia/Brisbane', b'Australia/Brisbane'), (b'Australia/Broken_Hill', b'Australia/Broken_Hill'), (b'Australia/Currie', b'Australia/Currie'), (b'Australia/Darwin', b'Australia/Darwin'), (b'Australia/Eucla', b'Australia/Eucla'), (b'Australia/Hobart', b'Australia/Hobart'), (b'Australia/Lindeman', b'Australia/Lindeman'), (b'Australia/Lord_Howe', b'Australia/Lord_Howe'), (b'Australia/Melbourne', b'Australia/Melbourne'), (b'Australia/Perth', b'Australia/Perth'), (b'Australia/Sydney', b'Australia/Sydney'), (b'Canada/Atlantic', b'Canada/Atlantic'), (b'Canada/Central', b'Canada/Central'), (b'Canada/Eastern', b'Canada/Eastern'), (b'Canada/Mountain', b'Canada/Mountain'), (b'Canada/Newfoundland', b'Canada/Newfoundland'), (b'Canada/Pacific', b'Canada/Pacific'), (b'Europe/Amsterdam', b'Europe/Amsterdam'), (b'Europe/Andorra', b'Europe/Andorra'), (b'Europe/Athens', b'Europe/Athens'), (b'Europe/Belgrade', b'Europe/Belgrade'), (b'Europe/Berlin', b'Europe/Berlin'), (b'Europe/Bratislava', b'Europe/Bratislava'), (b'Europe/Brussels', b'Europe/Brussels'), (b'Europe/Bucharest', b'Europe/Bucharest'), (b'Europe/Budapest', b'Europe/Budapest'), (b'Europe/Busingen', b'Europe/Busingen'), (b'Europe/Chisinau', b'Europe/Chisinau'), (b'Europe/Copenhagen', b'Europe/Copenhagen'), (b'Europe/Dublin', b'Europe/Dublin'), (b'Europe/Gibraltar', b'Europe/Gibraltar'), (b'Europe/Guernsey', b'Europe/Guernsey'), (b'Europe/Helsinki', b'Europe/Helsinki'), (b'Europe/Isle_of_Man', b'Europe/Isle_of_Man'), (b'Europe/Istanbul', b'Europe/Istanbul'), (b'Europe/Jersey', b'Europe/Jersey'), (b'Europe/Kaliningrad', b'Europe/Kaliningrad'), (b'Europe/Kiev', b'Europe/Kiev'), (b'Europe/Lisbon', b'Europe/Lisbon'), (b'Europe/Ljubljana', b'Europe/Ljubljana'), (b'Europe/London', b'Europe/London'), (b'Europe/Luxembourg', b'Europe/Luxembourg'), (b'Europe/Madrid', b'Europe/Madrid'), (b'Europe/Malta', b'Europe/Malta'), (b'Europe/Mariehamn', b'Europe/Mariehamn'), (b'Europe/Minsk', b'Europe/Minsk'), (b'Europe/Monaco', b'Europe/Monaco'), (b'Europe/Moscow', b'Europe/Moscow'), (b'Europe/Oslo', b'Europe/Oslo'), (b'Europe/Paris', b'Europe/Paris'), (b'Europe/Podgorica', b'Europe/Podgorica'), (b'Europe/Prague', b'Europe/Prague'), (b'Europe/Riga', b'Europe/Riga'), (b'Europe/Rome', b'Europe/Rome'), (b'Europe/Samara', b'Europe/Samara'), (b'Europe/San_Marino', b'Europe/San_Marino'), (b'Europe/Sarajevo', b'Europe/Sarajevo'), (b'Europe/Simferopol', b'Europe/Simferopol'), (b'Europe/Skopje', b'Europe/Skopje'), (b'Europe/Sofia', b'Europe/Sofia'), (b'Europe/Stockholm', b'Europe/Stockholm'), (b'Europe/Tallinn', b'Europe/Tallinn'), (b'Europe/Tirane', b'Europe/Tirane'), (b'Europe/Uzhgorod', b'Europe/Uzhgorod'), (b'Europe/Vaduz', b'Europe/Vaduz'), (b'Europe/Vatican', b'Europe/Vatican'), (b'Europe/Vienna', b'Europe/Vienna'), (b'Europe/Vilnius', b'Europe/Vilnius'), (b'Europe/Volgograd', b'Europe/Volgograd'), (b'Europe/Warsaw', b'Europe/Warsaw'), (b'Europe/Zagreb', b'Europe/Zagreb'), (b'Europe/Zaporozhye', b'Europe/Zaporozhye'), (b'Europe/Zurich', b'Europe/Zurich'), (b'GMT', b'GMT'), (b'Indian/Antananarivo', b'Indian/Antananarivo'), (b'Indian/Chagos', b'Indian/Chagos'), (b'Indian/Christmas', b'Indian/Christmas'), (b'Indian/Cocos', b'Indian/Cocos'), (b'Indian/Comoro', b'Indian/Comoro'), (b'Indian/Kerguelen', b'Indian/Kerguelen'), (b'Indian/Mahe', b'Indian/Mahe'), (b'Indian/Maldives', b'Indian/Maldives'), (b'Indian/Mauritius', b'Indian/Mauritius'), (b'Indian/Mayotte', b'Indian/Mayotte'), (b'Indian/Reunion', b'Indian/Reunion'), (b'Pacific/Apia', b'Pacific/Apia'), (b'Pacific/Auckland', b'Pacific/Auckland'), (b'Pacific/Chatham', b'Pacific/Chatham'), (b'Pacific/Chuuk', b'Pacific/Chuuk'), (b'Pacific/Easter', b'Pacific/Easter'), (b'Pacific/Efate', b'Pacific/Efate'), (b'Pacific/Enderbury', b'Pacific/Enderbury'), (b'Pacific/Fakaofo', b'Pacific/Fakaofo'), (b'Pacific/Fiji', b'Pacific/Fiji'), (b'Pacific/Funafuti', b'Pacific/Funafuti'), (b'Pacific/Galapagos', b'Pacific/Galapagos'), (b'Pacific/Gambier', b'Pacific/Gambier'), (b'Pacific/Guadalcanal', b'Pacific/Guadalcanal'), (b'Pacific/Guam', b'Pacific/Guam'), (b'Pacific/Honolulu', b'Pacific/Honolulu'), (b'Pacific/Johnston', b'Pacific/Johnston'), (b'Pacific/Kiritimati', b'Pacific/Kiritimati'), (b'Pacific/Kosrae', b'Pacific/Kosrae'), (b'Pacific/Kwajalein', b'Pacific/Kwajalein'), (b'Pacific/Majuro', b'Pacific/Majuro'), (b'Pacific/Marquesas', b'Pacific/Marquesas'), (b'Pacific/Midway', b'Pacific/Midway'), (b'Pacific/Nauru', b'Pacific/Nauru'), (b'Pacific/Niue', b'Pacific/Niue'), (b'Pacific/Norfolk', b'Pacific/Norfolk'), (b'Pacific/Noumea', b'Pacific/Noumea'), (b'Pacific/Pago_Pago', b'Pacific/Pago_Pago'), (b'Pacific/Palau', b'Pacific/Palau'), (b'Pacific/Pitcairn', b'Pacific/Pitcairn'), (b'Pacific/Pohnpei', b'Pacific/Pohnpei'), (b'Pacific/Port_Moresby', b'Pacific/Port_Moresby'), (b'Pacific/Rarotonga', b'Pacific/Rarotonga'), (b'Pacific/Saipan', b'Pacific/Saipan'), (b'Pacific/Tahiti', b'Pacific/Tahiti'), (b'Pacific/Tarawa', b'Pacific/Tarawa'), (b'Pacific/Tongatapu', b'Pacific/Tongatapu'), (b'Pacific/Wake', b'Pacific/Wake'), (b'Pacific/Wallis', b'Pacific/Wallis'), (b'US/Alaska', b'US/Alaska'), (b'US/Arizona', b'US/Arizona'), (b'US/Central', b'US/Central'), (b'US/Eastern', b'US/Eastern'), (b'US/Hawaii', b'US/Hawaii'), (b'US/Mountain', b'US/Mountain'), (b'US/Pacific', b'US/Pacific'), (b'UTC', b'UTC')])),
                ('check_for_updates', models.BooleanField(default=True, help_text=b'Periodically check for updates (<a href="https://kegbot.org/about/checkin">more info</a>)')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='KegTap',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text=b'The display name for this tap, for example, "Main Tap".', max_length=128)),
                ('description', models.TextField(help_text=b'User-visible description for this tap.', null=True, blank=True)),
                ('sort_order', models.PositiveIntegerField(default=0, help_text=b'Position relative to other taps when sorting (0=first).')),
                ('current_keg', models.OneToOneField(related_name='current_tap', null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Keg', help_text=b'Keg currently connected to this tap.')),
            ],
            options={
                'ordering': ('sort_order', 'id'),
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NotificationSettings',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('backend', models.CharField(help_text=b'Notification backend (dotted path) for these settings.', max_length=255)),
                ('keg_tapped', models.BooleanField(default=True, help_text=b'Sent when a keg is activated.')),
                ('session_started', models.BooleanField(default=False, help_text=b'Sent when a new drinking session starts.')),
                ('keg_volume_low', models.BooleanField(default=False, help_text=b'Sent when a keg becomes low.')),
                ('keg_ended', models.BooleanField(default=False, help_text=b'Sent when a keg has been taken offline.')),
                ('user', models.ForeignKey(help_text=b'User for these settings.', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Picture',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('image', models.ImageField(help_text=b'The image', upload_to=pykeg.core.models._pics_file_name)),
                ('time', models.DateTimeField(default=django.utils.timezone.now, help_text=b'Time/date of image capture')),
                ('caption', models.TextField(help_text=b'Caption for the picture, if any.', null=True, blank=True)),
                ('keg', models.ForeignKey(related_name='pictures', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Keg', help_text=b'Keg this picture was taken with, if any.', null=True)),
                ('session', models.ForeignKey(related_name='pictures', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.DrinkingSession', help_text=b'Session this picture was taken with, if any.', null=True)),
                ('user', models.ForeignKey(related_name='pictures', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'User that owns/uploaded this picture', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PluginData',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('plugin_name', models.CharField(help_text=b'Plugin short name', max_length=127)),
                ('key', models.CharField(max_length=127)),
                ('value', pykeg.core.jsonfield.JSONField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('time', models.DateTimeField(default=django.utils.timezone.now)),
                ('stats', pykeg.core.jsonfield.JSONField()),
                ('is_first', models.BooleanField(default=False, help_text=b'True if this is the most first record for the view.')),
                ('drink', models.ForeignKey(to='core.Drink')),
                ('keg', models.ForeignKey(related_name='stats', to='core.Keg', null=True)),
                ('session', models.ForeignKey(related_name='stats', to='core.DrinkingSession', null=True)),
                ('user', models.ForeignKey(related_name='stats', to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'get_latest_by': 'id',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='SystemEvent',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('kind', models.CharField(help_text=b'Type of event.', max_length=255, choices=[(b'drink_poured', b'Drink poured'), (b'session_started', b'Session started'), (b'session_joined', b'User joined session'), (b'keg_tapped', b'Keg tapped'), (b'keg_volume_low', b'Keg volume low'), (b'keg_ended', b'Keg ended')])),
                ('time', models.DateTimeField(help_text=b'Time of the event.')),
                ('drink', models.ForeignKey(related_name='events', blank=True, to='core.Drink', help_text=b'Drink involved in the event, if any.', null=True)),
                ('keg', models.ForeignKey(related_name='events', blank=True, to='core.Keg', help_text=b'Keg involved in the event, if any.', null=True)),
                ('session', models.ForeignKey(related_name='events', blank=True, to='core.DrinkingSession', help_text=b'Session involved in the event, if any.', null=True)),
                ('user', models.ForeignKey(related_name='events', blank=True, to=settings.AUTH_USER_MODEL, help_text=b'User responsible for the event, if any.', null=True)),
            ],
            options={
                'ordering': ('-id',),
                'get_latest_by': 'time',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Thermolog',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('temp', models.FloatField()),
                ('time', models.DateTimeField()),
            ],
            options={
                'ordering': ('-time',),
                'get_latest_by': 'time',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ThermoSensor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('raw_name', models.CharField(max_length=256)),
                ('nice_name', models.CharField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='thermolog',
            name='sensor',
            field=models.ForeignKey(to='core.ThermoSensor'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='stats',
            unique_together=set([('drink', 'user', 'keg', 'session')]),
        ),
        migrations.AlterUniqueTogether(
            name='plugindata',
            unique_together=set([('plugin_name', 'key')]),
        ),
        migrations.AlterUniqueTogether(
            name='notificationsettings',
            unique_together=set([('user', 'backend')]),
        ),
        migrations.AddField(
            model_name='kegtap',
            name='temperature_sensor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.ThermoSensor', help_text=b'Optional sensor monitoring the temperature at this tap.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='kegbotsite',
            name='background_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Picture', help_text=b'Background for this site.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flowtoggle',
            name='tap',
            field=models.OneToOneField(related_name='toggle', null=True, blank=True, to='core.KegTap', help_text=b'Tap to which this toggle is currently bound.'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='flowtoggle',
            unique_together=set([('controller', 'port_name')]),
        ),
        migrations.AddField(
            model_name='flowmeter',
            name='tap',
            field=models.OneToOneField(related_name='meter', null=True, blank=True, to='core.KegTap', help_text=b'Tap to which this meter is currently bound.'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='flowmeter',
            unique_together=set([('controller', 'port_name')]),
        ),
        migrations.AddField(
            model_name='drink',
            name='keg',
            field=models.ForeignKey(related_name='drinks', on_delete=django.db.models.deletion.PROTECT, editable=False, to='core.Keg', help_text=b'Keg against which this Drink is accounted.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='drink',
            name='picture',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Picture', help_text=b'Picture snapped with this drink.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='drink',
            name='session',
            field=models.ForeignKey(related_name='drinks', on_delete=django.db.models.deletion.PROTECT, blank=True, editable=False, to='core.DrinkingSession', help_text=b'Session where this Drink is grouped.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='drink',
            name='user',
            field=models.ForeignKey(related_name='drinks', editable=False, to=settings.AUTH_USER_MODEL, help_text=b'User responsible for this Drink, or None if anonymous/unknown.'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beverageproducer',
            name='picture',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Picture', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beverage',
            name='picture',
            field=models.ForeignKey(blank=True, to='core.Picture', help_text=b'Label image.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='beverage',
            name='producer',
            field=models.ForeignKey(to='core.BeverageProducer'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='authenticationtoken',
            unique_together=set([('auth_device', 'token_value')]),
        ),
        migrations.AddField(
            model_name='apikey',
            name='device',
            field=models.ForeignKey(to='core.Device', help_text=b'Device this key is associated with.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='apikey',
            name='user',
            field=models.ForeignKey(blank=True, to=settings.AUTH_USER_MODEL, help_text=b'User receiving API access.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='mugshot',
            field=models.ForeignKey(related_name='user_mugshot', on_delete=django.db.models.deletion.SET_NULL, blank=True, to='core.Picture', null=True),
            preserve_default=True,
        ),
    ]
