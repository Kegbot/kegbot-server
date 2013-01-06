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

import sys

def progbar(title, pos, total, width=40):
  """Prints a progress bar to stdout.

  Args
    title: title to show next to progress bar
    pos: current position (integer)
    total: total positions (integer)
    width: width of the progres bar, in characters
  """
  if not total:
    chars = width
  else:
    chars = int((float(pos)/total)*width)
  rem = width - chars
  inner = '+'*chars + ' '*rem
  sys.stdout.write('%-30s  [%s] %i/%i\r' % (title, inner, pos, total))
  sys.stdout.flush()


