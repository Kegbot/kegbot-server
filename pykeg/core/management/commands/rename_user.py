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

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.db import transaction

from pykeg.core import models


class Command(BaseCommand):
    args = '<from> <to>'
    help = 'Renames user from <from> to <to>.'

    def handle(self, *args, **options):
        if len(args) < 2:
            raise CommandError('Must specify <from> and <to>')

        from_username = args[0]
        to_username = args[1]

        if from_username == 'guest':
            raise CommandError('Cannot rename the guest user.')

        with transaction.atomic():
            try:
                user = models.User.objects.get(username=from_username)
            except models.User.DoesNotExist:
                raise CommandError('User named "{}" does not exist'.format(from_username))

            user.username = to_username
            user.save()

        print '"{}" has been renamed "{}"'.format(from_username, to_username)
