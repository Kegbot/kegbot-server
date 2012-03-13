# Copyright 2009 Mike Wakerly <opensource@hoho.com>
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

import random

from django.db import models
from django.contrib.auth.models import User

from pykeg.core import models as core_models
from pykeg.core import units

class UserUntappdLink(models.Model):
  """Maps a user to a particular Untappd account."""
  user_profile = models.OneToOneField(core_models.UserProfile, primary_key=True)
  untappd_name = models.CharField(max_length=256)
  untappd_password_hash = models.CharField(max_length=128)
