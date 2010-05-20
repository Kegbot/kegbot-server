# Copyright 2010 Mike Wakerly <opensource@hoho.com>
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

import os
import random

from django.db import models
from django.contrib.auth.models import User

def sound_file_name(instance, filename):
  rand_salt = random.randrange(0xffff)
  new_filename = '%04x-%s' % (rand_salt, filename)
  return os.path.join('sounds', new_filename)


class SoundFile(models.Model):
  sound = models.FileField(upload_to=sound_file_name)
  title = models.CharField(max_length=128)
  active = models.BooleanField(default=True)

  def __str__(self):
    return '%s (%s)' % (self.title, self.sound)


class SoundEvent(models.Model):
  event_name = models.CharField(max_length=256)
  event_predicate = models.CharField(max_length=256, blank=True, null=True)
  soundfile = models.ForeignKey(SoundFile)
  user = models.ForeignKey(User, blank=True, null=True)

  def SoundTitle(self):
    return self.soundfile.title

  def __str__(self):
    return '%s(%s) -> %s' % (self.event_name, self.event_predicate,
        self.soundfile.title)
