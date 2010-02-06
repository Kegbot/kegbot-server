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

"""Wrapper module for database implementation."""

import logging

from pykeg.core import kb_common
from pykeg.core import config
from pykeg.core import models

class KegbotBackend(object):
  def __init__(self):
    self._logger = logging.getLogger('backend')
    self._config = config.KegbotConfig()

  def GetConfig(self):
    return self._config

  def GetDefaultUser(self):
    """Return a |User| instance to use for unknown pours."""
    DEFAULT_USER_LABELNAME = '__default_user__'

    label_q = models.UserLabel.objects.filter(labelname=DEFAULT_USER_LABELNAME)
    if not len(label_q):
      raise kb_common.ConfigurationError, ('Default user label "%s" not found.' % DEFAULT_USER_LABELNAME)

    user_q = label_q[0].userprofile_set.all()
    if not len(user_q):
      raise kb_common.ConfigurationError, ('No users found with label "%s"; need at least one.' % DEFAULT_USER_LABELNAME)

    default_user = user_q[0].user
    self._logger.info('Default user for unknown flows: %s' % str(default_user))
    return default_user

  def CheckSchemaVersion(self):
    # TODO(mikey): use South to determine if there are any pending migrations.
    pass

  def GetUserFromUsername(self, username):
    matches = models.User.objects.filter(username=username)
    if not matches.count() == 1:
      return None
    return matches[0]

  @classmethod
  def CreateNewUser(cls, username, gender=kb_common.DEFAULT_NEW_USER_GENDER,
      weight=kb_common.DEFAULT_NEW_USER_WEIGHT):
    u = models.User(username=username)
    u.save()
    p = u.get_profile()
    p.gender = gender
    p.weight = weight
    p.save()
    return u
