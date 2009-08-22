# Copyright 2003-2009 Mike Wakerly <opensource@hoho.com>
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

from pykeg.core import backend
from pykeg.core import models
from pykeg.core import units


def db_is_installed():
  try:
    version = models.Config.objects.get(key='db.schema_version')
    return True
  except models.Config.DoesNotExist:
    return False

def add_label(user, labelname):
  res = models.UserLabel.objects.filter(labelname__exact=labelname)
  if len(res):
    l = res[0]
  else:
    l = models.UserLabel(labelname=labelname)
    l.save()
  user.get_profile().labels.add(l)

def set_defaults():
  """ default values (contents may change with schema) """
  if db_is_installed():
    raise RuntimeError, "Database is already installed."

  # config table defaults
  default_config = (
     ('logging.logfile', 'keg.log'),
     ('logging.logformat', '%(asctime)s %(levelname)-8s (%(name)s) %(message)s'),
     ('logging.use_logfile', 'true'),
     ('logging.use_stream', 'true'),
     ('db.schema_version', str(models.SCHEMA_VERSION)),
  )
  for key, val in default_config:
     rec = models.Config(key=key, value=val)
     rec.save()

  # user defaults
  guest_user = backend.KegbotBackend.CreateNewUser('guest')

  # brewer defaults
  unk_brewer = models.Brewer(name='Unknown Brewer')
  unk_brewer.save()

  # beerstyle defaults
  unk_style = models.BeerStyle(name='Unknown Style')
  unk_style.save()

  # beertype defaults
  unk_type = models.BeerType(name="Unknown Beer", brewer=unk_brewer, style=unk_style)
  unk_type.save()

  # userlabel defaults
  add_label(guest_user, '__default_user__')
  add_label(guest_user, '__no_bac__')

  # KegSize defaults - from http://en.wikipedia.org/wiki/Keg#Size
  default_sizes = (
    (15.5, "Full Keg (half barrel)"),
    (13.2, "Import Keg (European barrel)"),
    (7.75, "Pony Keg (quarter barrel)"),
    (6.6, "European Half Barrel"),
    (5.23, "Sixth Barrel (torpedo keg)"),
    (5.0, "Corny Keg"),
    (1.0, "Mini Keg"),
  )
  for gallons, description in default_sizes:
    volume = units.Quantity(gallons, units.UNITS.USGallon)
    volume_int = volume.Amount(in_units=units.RECORD_UNIT)

    ks = models.KegSize(
      name=description,
      volume=volume_int,
    )
    ks.save()

