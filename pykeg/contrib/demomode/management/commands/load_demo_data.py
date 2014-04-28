# Copyright 2014 Bevbot LLC, All Rights Reserved
#
# This file is part of the Pykeg package of the Kegbot project.
# For more information on Pykeg or Kegbot, see http://kegbot.org/
#
# Pykeg is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# Pykeg is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Pykeg.  If not, see <http://www.gnu.org/licenses/>.

import json
import os.path
import random
import datetime
from collections import deque
from uuid import uuid1

from django.core.files import File
from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone

from pykeg.contrib.demomode.views import random_item
from pykeg.backend import get_kegbot_backend
from pykeg.core import defaults
from pykeg.core import models


NUM_SESSIONS = 30
MINUTES_IN_DAY = 60 * 24

MINIMUM_POUR_SIZE_ML = 100
MAXIMUM_POUR_SIZE_ML = 450

"""Generates a bunch of fake drinks from a configuration."""


class LoadDemoDataCommand(BaseCommand):
    args = '<demo_data_dir>'
    help = 'Inserts demo data into the database'

    def handle(self, *args, **options):
        if len(args) < 1:
            raise CommandError('Must specify demo data directory')

        data_dir = os.path.abspath(args[0])
        demo_data = self.load_demo_data(data_dir)

        with transaction.atomic():
            if models.User.objects.all().count() or models.Drink.objects.all().count():
                raise CommandError('Database is already loaded.')

            defaults.set_defaults(set_is_setup=True)

            # Install demo data.
            for username in demo_data['drinkers']:
                user = models.User.objects.create_superuser(username=username, email=None, password=username)

                picture_path = os.path.join(data_dir, 'pictures', 'drinkers', username, 'mugshot.png')
                if os.path.exists(picture_path):
                    p = self.create_picture(picture_path, user=user)
                    user.mugshot = p
                    user.save()

            for beverage in demo_data['beverages']:
                brewer, _ = models.BeverageProducer.objects.get_or_create(name=beverage['brewer_name'])
                beer, _ = models.Beverage.objects.get_or_create(name=beverage['name'], beverage_type='beer',
                    producer=brewer, style=beverage['style'])

                picture_path = beverage.get('image')
                if picture_path:
                    picture = self.create_picture(os.path.join(data_dir, picture_path))
                    beer.picture = picture
                    beer.save()
                else:
                    raise ValueError('No pic for brewer!')

            sessions = self.build_random_sessions(models.User.objects.all(),
                NUM_SESSIONS, demo_data['shouts'])

            minutes = sessions[-1][0]
            minutes += MINUTES_IN_DAY
            minutes -= (minutes % (MINUTES_IN_DAY))

            session_start = timezone.now()
            session_start -= datetime.timedelta(hours=session_start.hour + 4,
                minutes=session_start.minute,
                seconds=session_start.second)
            session_start -= datetime.timedelta(minutes=minutes)

            for minute, drinker, volume_ml, shout in sessions:
                date = session_start + datetime.timedelta(minutes=minute)

                picture_path = None
                if random.random() >= 0.25:
                    d = demo_data['pictures'].get(drinker.username)
                    if d:
                        picture_path = d[0]
                        d.rotate()
                self.do_pour(drinker, date, volume_ml, shout, picture_path)

            print 'Demo data loaded.'

    def do_pour(self, user, when, volume_ml, shout, picture_path):
        be = get_kegbot_backend()
        tap = random_item(models.KegTap)

        # End keg if it's near empty.
        if tap.current_keg and tap.current_keg.remaining_volume_ml() < volume_ml:
            be.end_keg(tap)

        # Start keg if the tap is idle.
        if not tap.current_keg:
            beverage = random_item(models.Beverage)
            be.start_keg(tap, beverage=beverage)

        drink = be.record_drink(tap, ticks=0, volume_ml=volume_ml,
            username=user.username, pour_time=when, shout=shout)

        if picture_path:
            p = self.create_picture(picture_path, user=user,
                session=drink.session, keg=drink.keg)
            drink.picture = p
            drink.save()
        return drink

    def create_picture(self, path, **kwargs):
        f = File(open(path, 'r'))
        p = models.Picture(image=f, **kwargs)
        name = '%s%s' % (uuid1(), os.path.splitext(f.name)[1])
        p.image.save(name, f)
        p.save()
        return p

    def build_random_sessions(self, all_drinkers, count, shouts):
        MIN_POUR_ML = 200
        MAX_POUR_ML = 500

        pours = []
        minute = 0

        for session_number in xrange(count):
            session = []
            num_drinkers = random.randint(1, len(all_drinkers))
            drinkers = random.sample(all_drinkers, num_drinkers)

            # Drink a little more when others are joining
            session_max = 1000 + min(2000, 500 * len(drinkers))

            for drinker in drinkers:
                subminute = random.randint(0, 15)
                session_total = random.randint(500, session_max)
                session_remain = session_total

                while session_remain > 0:
                    if session_remain <= MIN_POUR_ML:
                        drink_volume = session_remain
                    else:
                        drink_volume = random.randint(MIN_POUR_ML, MAX_POUR_ML)

                    shout = ''
                    if shouts and random.random() >= 0.60:
                        shout = shouts[0]
                        shouts.rotate(1)

                    session.append((minute + subminute, drinker, drink_volume, shout))
                    subminute += int(drink_volume / 40) + random.randint(0, 30)  # 40 mL/minute min plus noise
                    session_remain -= drink_volume

            # session.sort()
            # for minute, drinker, volume, shout in session:
            #     print '%08s %016s %04s  %s' % (minute, drinker, volume, shout)
            # print ''

            pours += session

            # wait 1 - 3 days for next session
            minute += random.randint(1, 3) * MINUTES_IN_DAY
            minute -= (minute % (MINUTES_IN_DAY))
            minute += random.randint(-120, 120)

        pours.sort()
        return pours

    def load_demo_data(self, path):
        demo_data_file = os.path.join(path, 'demo_data.json')
        if not os.path.isfile(demo_data_file):
            raise CommandError('Missing demo_data file: %s' % demo_data_file)

        demo_data = json.loads(open(demo_data_file).read())
        demo_data['pictures'] = {}

        for drinker_name in demo_data['drinkers']:
            demo_data['pictures'][drinker_name] = deque()

            pictures_dir = os.path.join(path, 'pictures', 'drinkers', drinker_name)
            if not os.path.isdir(pictures_dir):
                continue

            for picture_name in (p for p in os.listdir(pictures_dir) if not p.startswith('.')):
                if picture_name == 'mugshot.png':
                    continue
                picture_path = os.path.join(pictures_dir, picture_name)
                demo_data['pictures'][drinker_name].append(picture_path)
            random.shuffle(demo_data['pictures'][drinker_name])

        demo_data['shouts'] = deque(demo_data['shouts'])
        random.shuffle(demo_data['shouts'])

        return demo_data

Command = LoadDemoDataCommand
