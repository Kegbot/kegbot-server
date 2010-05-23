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

"""Miscellanous configuration from the database."""

class KegbotConfig:
  def __init__(self, configdict):
    self._configdict = configdict

  def get(self, option, default=None):
    return self._configdict.get(option, default)

  def getboolean(self, option):
    val = self.get(option, 'false')
    if val.lower() == 'true' or val == '1':
      return True
    return False

  def IsFeatureEnabled(self, feature_name):
    key = '.'.join(('feature', feature_name, 'enable'))
    return self.getboolean(key)

