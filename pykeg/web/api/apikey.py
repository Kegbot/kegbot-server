# Copyright 2011 Mike Wakerly <opensource@hoho.com>
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

class ApiKey:
  """
  Format
    VRRRUUUUSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS
    V = Version (1 hex digit)
    R = Reserved (3 hex digits, zeroes)
    U = UID (4 hex digits)
    S = Secret (32 chars)
  40 characters
  """
  VERSION = 1

  def __init__(self, uid, secret=None):
    self._uid = uid
    if secret is None:
      secret = ApiKey.NewSecret()
    self._secret = secret

  def __str__(self):
    return self.Encode()

  def Encode(self):
    return ApiKey._EncodeParts(self._uid, self._secret)

  def uid(self):
    return self._uid

  def secret(self):
    return self._secret

  @classmethod
  def FromString(cls, s):
    if s is None:
      raise ValueError("Must provide a string.")

    if len(s) != 40:
      raise ValueError("Bad key length.")

    version = s[0]
    reserved = s[1:4]
    uidstr = s[4:8]
    secret = s[8:]

    if version != str(ApiKey.VERSION):
      raise ValueError("Bad key version.")
    if reserved != '000':
      raise ValueError("Illegal value for reserved field: '%s'" % reserved)
    uid = int(uidstr, 16)

    return ApiKey(uid, secret)

  @classmethod
  def NewSecret(cls):
    return '%032x' % random.randint(0, 2**128 - 1)

  @classmethod
  def _EncodeParts(cls, uid, secret):
    if len(secret) != 32:
      raise ValueError, "Bad secret length"
    result = '%01i%03i%04x%s' % (cls.VERSION, 0, uid, secret)
    return result

