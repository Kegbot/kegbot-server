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

import copy
import datetime
import pytz

from django.conf import settings
from django.core import urlresolvers
from django.core.urlresolvers import NoReverseMatch
from django.core.urlresolvers import reverse
from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Variable
from django.utils.safestring import mark_safe

from pykeg.core import kbjson
from pykeg.core import models
from pykeg.core import units
from pykeg.web.charts import charts

register = Library()

@register.inclusion_tag('kegweb/mugshot_box.html', takes_context=True)
def mugshot_box(context, user, boxsize=0):
  c = copy.copy(context)
  c['user'] = user
  c['boxsize'] = boxsize
  return c

@register.inclusion_tag('kegweb/page_block.html')
def render_page(page):
  return {'page' : page}

### navitem

@register.tag('navitem')
def navitem(parser, token):
  """{% navitem <viewname> <title> [exact] %}"""
  tokens = token.split_contents()
  if len(tokens) < 3:
    raise TemplateSyntaxError, '%s requires at least 3 tokens' % tokens[0]
  return NavitemNode(*tokens[1:])

class NavitemNode(Node):
  def __init__(self, *args):
    self._viewname = args[0]
    self._title = args[1]
    self._exact = 'exact' in args[2:]

  def render(self, context):
    viewname = self._viewname
    title = Variable(self._title).resolve(context)
    kbsite = context['kbsite']
    try:
      urlbase = reverse(viewname, args=[kbsite.url()])
    except NoReverseMatch, e:
      urlbase = reverse(viewname)

    request_path = context['request_path']

    if self._exact:
      active = (request_path == urlbase)
    else:
      active = request_path.startswith(urlbase)
    if active:
      res = '<li class="active">'
    else:
      res = '<li>'
    res += '<a href="%s">%s</a></li>' % (urlbase, title)
    return res


### timeago

@register.tag('timeago')
def timeago(parser, token):
  """{% timeago <timestamp> %}"""
  tokens = token.contents.split()
  if len(tokens) != 2:
    raise TemplateSyntaxError, '%s requires 2 tokens' % tokens[0]
  return TimeagoNode(tokens[1])

class TimeagoNode(Node):
  def __init__(self, timestamp_varname):
    self._timestamp_varname = timestamp_varname

  def render(self, context):
    tv = Variable(self._timestamp_varname)
    ts = tv.resolve(context)

    # Try to set time zone information.
    if settings.TIME_ZONE:
      try:
        tz = pytz.timezone(settings.TIME_ZONE)
        ts = tz.localize(ts)
      except pytz.UnknownTimeZoneError:
        pass

    iso = ts.isoformat()
    alt = ts.strftime("%A, %B %d, %Y %I:%M%p")
    return '<abbr class="timeago" title="%s">%s</abbr>' % (iso, alt)


### volume

@register.tag('volume')
def volumetag(parser, token):
  """{% volume <amount> %}"""
  tokens = token.contents.split()
  if len(tokens) < 2:
    raise TemplateSyntaxError, '%s requires at least 2 tokens' % tokens[0]
  return VolumeNode(tokens[1], tokens[2:])

class VolumeNode(Node):
  TEMPLATE = """
    <span class="hmeasure" title="%(title)s">
      <span class="num">%(num)s</span>
      <span class="unit">%(unit)s</span>
    </span>""".strip()

  def __init__(self, volume_varname, extra_args):
    self._volume_varname = volume_varname
    self._extra_args = extra_args

  def render(self, context):
    tv = Variable(self._volume_varname)
    num = tv.resolve(context)
    unit = 'mL'
    title = '%s %s' % (float(num), unit)
    return VolumeNode.TEMPLATE % vars()

### chart

@register.tag('chart')
def chart(parser, tokens):
  """{% chart <charttype> <obj> width height %}"""
  tokens = tokens.contents.split()
  if len(tokens) < 4:
    raise TemplateSyntaxError('chart requires at least 4 arguments')
  charttype = tokens[1]
  try:
    width = int(tokens[-2])
    height = int(tokens[-1])
  except ValueError:
    raise TemplateSyntaxError('invalid width or height')
  args = tokens[2:-2]
  return ChartNode(charttype, width, height, args)

class ChartNode(Node):
  CHART_TMPL = '''
  <!-- begin chart %(chart_id)s -->
  <div id="chart-%(chart_id)s-container"
      style="height: %(height)spx; width: %(width)spx;"
      class="kb-chartbox"></div>
  <script type="text/javascript">
    var chart_%(chart_id)s;
    $(document).ready(function() {
      var chart_data = %(chart_data)s;
      chart_%(chart_id)s = new Highcharts.Chart(chart_data);
    });
  </script>
  <!-- end chart %(chart_id)s -->

  '''
  ERROR_TMPL = '''
  <!-- begin chart %(chart_id)s -->
  <div id="chart-%(chart_id)s-container"
      style="height: %(height)spx; width: %(width)spx;"
      class="kb-chartbox-error">
    %(error_str)s
  </div>
  <!-- end chart %(chart_id)s -->
  '''
  def __init__(self, charttype, width, height, args):
    self._charttype = charttype
    self._width = width
    self._height = height
    self._args = args

    try:
      self._chart_fn = getattr(self, 'chart_%s' % (self._charttype,))
    except AttributeError:
      raise TemplateSyntaxError('unknown chart type: %s' % self._charttype)

  def _get_chart_id(self, context):
    # TODO(mikey): Is there a better way to store _CHART_ID?
    if not hasattr(context, '_CHART_ID'):
      context._CHART_ID = 0
    context._CHART_ID += 1
    return context._CHART_ID

  def render(self, context):
    chart_id = self._get_chart_id(context)

    width = self._width
    height = self._height

    obj = Variable(self._args[0]).resolve(context)
    try:
      chart_result = self._chart_fn(obj)
    except charts.ChartError, e:
      error_str = 'chart error: %s' % (e,)
      return ChartNode.ERROR_TMPL % vars()
    chart_base = {
      'chart': {
        'borderColor': '#eeeeff',
        'borderWidth': 0,
        'renderTo': 'chart-%s-container' % chart_id,
      },
      'credits': {
        'enabled': False,
      },
      'legend': {
        'enabled': False,
      },
      'margin': [0, 0, 0, 0],
      'title': {
        'text': None,
      },
      'yAxis': {
        'labels': {
          'align': 'left'
        },
        'title': {
          'text': None,
        }
      },
    }

    chart_data = chart_base
    for k, v in chart_result.iteritems():
      if k not in chart_data:
        chart_data[k] = v
      elif type(v) == type({}):
        chart_data[k].update(v)
      else:
        chart_data[k] = v
    chart_data = kbjson.dumps(chart_data, indent=None)
    return ChartNode.CHART_TMPL % vars()

  def chart_sensor(self, obj):
    """Shows a simple line plot of a specific temperature sensor.

    Args:
      obj - the models.ThermoSensor to plot
    """
    return charts.TemperatureSensorChart(obj)

  def chart_keg_volume(self, obj):
    """Shows a horizontal bar chart of keg served/remaining volume.

    Args:
      obj - the models.Keg instance to chart
    """
    return charts.KegVolumeChart(obj)

  def chart_volume_by_day(self, obj):
    """Shows keg or session usage by day of the week.

    Args:
      obj - the stats instance to chart
    """
    return charts.VolumeByWeekday(obj)

  def chart_sessions_weekday(self, obj):
    """Vertical bar chart showing session volume by day of week.

    Args:
      obj - an iterable of models.DrinkingSession or
            models.UserDrinkingSessionPart instances
    """
    return charts.UserSessionsByWeekday(obj)

  def chart_sessions_volume(self, obj):
    """Line chart showing session volumes.

    Args:
      obj - an iterable of models.DrinkingSession or
            models.UserDrinkingSessionPart instances
    """
    return charts.SessionVolumes(obj)

  def chart_users_by_volume(self, obj):
    """Pie chart showing users by volume.

    Args:
      obj - the stats instance to chart
    """
    return charts.UsersByVolume(obj)

  def chart_user_session_chunks(self, obj):
    """Show's a single user's activity within a session.

    Args:
      obj - the models.UserSessionChunk for the user/session to chart
    """
    return charts.UserSessionChunks(obj)

@register.filter
def volume(text, fmt='pints'):
  try:
    vol = units.Quantity(float(text))
  except ValueError:
    return text
  if fmt == 'pints':
    res = vol.InPints()
  elif fmt == 'liters':
    res = vol.InLiters()
  elif fmt == 'ounces':
    res = vol.InOunces()
  elif fmt == 'gallons':
    res = vol.InUSGallons()
  elif fmt == 'twelveounces':
    res = vol.InTwelveOunceBeers()
  elif fmt == 'halfbarrels':
    res = vol.InHalfBarrelKegs()
  else:
    raise TemplateSyntaxError, 'Unknown volume format: %s' % fmt
  return float(res)

@register.filter
def bac_format(text):
  try:
    f = float(text)
  except ValueError:
    return ''
  BAC_MAX = 0.16
  STEPS = 32
  colors = ['#%02x0000' % (x*8,) for x in range(STEPS)]
  bacval = min(max(0, f), BAC_MAX)
  colorstep = BAC_MAX/float(STEPS)
  color = colors[min(STEPS-1, int(bacval/colorstep))]
  ret = '<font color="%s">%.3f</font>' % (color, f)
  if f > 0.08:
    ret = '<b>%s</b>' % ret
  return mark_safe(ret)

@register.filter
def datetime_js(val):
  if not isinstance(val, datetime.datetime):
    return "new Date(1970,0,1)"
  vals = map(str, (
      val.year,
      val.month - 1,
      val.day,
      val.hour,
      val.minute,
      val.second))
  return "new Date(%s)" % (",".join(vals))
