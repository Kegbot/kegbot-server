import datetime

try:
  import pygooglechart
  HAVE_GOOGLE_CHART = True
except ImportError:
  HAVE_GOOGLE_CHART = False

from django.core import urlresolvers
from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Variable
from django.utils.safestring import mark_safe

from pykeg.core import models
from pykeg.core import units
from pykeg.web.kegweb import stats

class KegweblibError(Exception):
  """Base kegweblib execption."""

class ChartUnavailableError(KegweblibError):
  """Thrown when a chart cannot be rendered."""

register = Library()

def mugshot_box(user, boxsize=100):
  if user:
    img_url = user.get_profile().MugshotUrl()
    user_url = urlresolvers.reverse('drinker', args=(user.username,))
  else:
    img_url = urlresolvers.reverse('site-media',
        args=('images/unknown-drinker.png',))
    user_url = ''

  return {
      'user' : user,
      'boxsize' : boxsize,
      'user_url' : user_url,
      'img_url': img_url,
  }
register.inclusion_tag('kegweb/mugshot_box.html')(mugshot_box)

def render_page(page):
  return {'page' : page}
register.inclusion_tag('kegweb/page_block.html')(render_page)

def timeago(parser, token):
  """{% timeago <timestamp> %}"""
  tokens = token.contents.split()
  if len(tokens) != 2:
    raise TemplateSyntaxError, '%s requires 2 tokens' % tokens[0]
  return TimeagoNode(tokens[1])
register.tag('timeago', timeago)

class TimeagoNode(Node):
  def __init__(self, timestamp_varname):
    self._timestamp_varname = timestamp_varname

  def render(self, context):
    tv = Variable(self._timestamp_varname)
    ts = tv.resolve(context)

    iso = ts.isoformat()
    alt = ts.strftime("%A, %B %d, %Y %I:%M%p")
    return '<abbr class="timeago" title="%s">%s</abbr>' % (iso, alt)

def chart(parser, tokens):
  """{% chart <charttype> [args] width height %}"""
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

register.tag('chart', chart)

class ChartNode(Node):
  def __init__(self, charttype, width, height, args):
    self._charttype = charttype
    self._width = width
    self._height = height
    self._args = args

    self._chart_fn = getattr(self, 'chart_%s' % (self._charttype,))
    if not self._chart_fn:
      raise TemplateSyntaxError('unknown chart type: %s' % self._charttype)

  def render(self, context):
    try:
      if not HAVE_GOOGLE_CHART:
        raise ChartUnavailableError, "chart library unavailable"
      url = self._chart_fn(context)
      res = '<div class="kb-chart"><img src="%s"/></div>' % url
    except ChartUnavailableError, e:
      reason = str(e)
      res = ('<div class="kb-chart-missing" '
          'style="width:%ipx; height:%ipx;">%s'
          '</div>' % (self._width, self._height, reason))
    return res

  def chart_sensor(self, context):
    """ Shows a simple line plot of a specific temperature sensor.

    Syntax:
      {% chart sensor <sensorname> width height %}
    Args:
      sensorname - the nice_name of a ThermoSensor
    """
    sensor_name_var = Variable(self._args[0])
    sensor_name = sensor_name_var.resolve(context)

    try:
      sensor = models.ThermoSensor.objects.get(nice_name=sensor_name)
    except models.ThermoSensor.DoesNotExist:
      raise ChartUnavailableError, "Sensor '%s' not found" % sensor_name

    hours = 12
    now = datetime.datetime.now()
    start = now - (datetime.timedelta(hours=hours))
    start = start - (datetime.timedelta(seconds=start.second))

    points = sensor.thermolog_set.filter(time__gte=start).order_by('time')

    curr = start
    temps = []
    have_temps = False
    for point in points:
      while curr <= point.time:
        curr += datetime.timedelta(minutes=1)
        if curr < point.time:
          temps.append(None)
        else:
          temps.append(point.temp)
          have_temps = True

    if not have_temps:
      raise ChartUnavailableError, "Not enough data"

    chart = pygooglechart.SparkLineChart(self._width, self._height)
    chart.add_data(temps)
    chart.fill_solid(pygooglechart.Chart.BACKGROUND, '00000000')
    chart.set_colours(['4D89F9'])
    return chart.get_url()

  def _get_keg_stats(self, context):
    keg_var = Variable(self._args[0])
    keg = keg_var.resolve(context)

    if not keg or not isinstance(keg, models.Keg):
      raise ChartUnavailableError, "Argument is not a Keg instance"

    stats = keg.GetStats()
    if not stats:
      raise ChartUnavailableError, "Stats unavailable"
    return keg, stats

  def chart_keg_volume(self, context):
    """ Shows a horizontal bar chart of keg served/remaining volume.

    Syntax:
      {% chart keg_volume <keg> width height %}
    Args:
      keg - the keg instance to chart
    """
    keg, stats = self._get_keg_stats(context)

    served = units.Quantity(stats.get('total-volume', 0.0))
    served_pints = served.ConvertTo.Pint
    full_pints = keg.full_volume().ConvertTo.Pint
    remain_pints = full_pints - served_pints

    chart = pygooglechart.StackedHorizontalBarChart(self._width, self._height,
        x_range=(0, full_pints))
    chart.set_bar_width(20)
    chart.set_colours(['4D89F9','C6D9FD'])
    chart.add_data([min(served_pints, full_pints)])
    chart.add_data([full_pints])
    return chart.get_url()

  def chart_keg_volume_by_day(self, context):
    """ Shows a horizontal bar chart of keg served/remaining volume.

    Syntax:
      {% chart keg_volume_by_day <keg> width height %}
    Args:
      keg - the keg instance to chart
    """
    keg, stats = self._get_keg_stats(context)

    volmap = stats.get('volume-by-day-of-week')
    if not volmap:
      raise ChartUnavailableError, "Daily volumes unavailable"

    vals = []
    for k in sorted(volmap.keys()):
      vals.append(float(volmap[k]))
    if len(vals) != 7:
      raise ChartUnavailableError, "Volume data is corrupt"
    chart = self._day_of_week_chart(vals)
    return chart.get_url()


  def _day_of_week_chart(self, vals):
    chart = pygooglechart.StackedVerticalBarChart(self._width, self._height)
    chart.set_bar_width(20)
    chart.set_colours(['4D89F9','C6D9FD'])

    # convert from 0=Monday to 0=Sunday
    vals.insert(0, vals.pop(-1))

    chart.add_data(vals)
    labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    chart.set_axis_labels('x', labels)
    return chart

  def chart_sessions_weekday(self, context):
    """ Vertical bar chart showing session volume by day of week.

    Syntax:
      {% chart sessions_weekday <sessions> width height %}
    Args:
      sessions - an iterable of DrinkingSession or UserDrinkingSessionPart
                 instances
    """
    sessions_var = Variable(self._args[0])
    sessions = sessions_var.resolve(context)
    if not sessions:
      raise ChartUnavailableError, "Must give sessions as argument"

    weekdays = [0] * 7

    for sess in sessions:
      date = int(sess.starttime.strftime('%w'))
      weekdays[date] += int(sess.Volume())
    chart = self._day_of_week_chart(weekdays)
    return chart.get_url()

  def chart_sessions_volume(self, context):
    """ Line chart showing session volumes.

    Syntax:
      {% chart sessions_volume <sessions> width height %}
    Args:
      sessions - an iterable of DrinkingSession or UserDrinkingSessionPart
                 instances
    """
    sessions_var = Variable(self._args[0])
    sessions = sessions_var.resolve(context)
    if not sessions:
      raise ChartUnavailableError, "Must give sessions as argument"

    data = []
    avgs = []
    avg_points = []
    total = 0.0
    for sess in sessions:
      vol = int(sess.Volume())
      data.append(vol)
      avg_points.append(vol)
      avg_points = avg_points[-5:]
      avgs.append(sum(avg_points) / len(avg_points))

    chart = pygooglechart.SimpleLineChart(self._width, self._height)
    chart.set_colours(['4D89F9','C6D9FD'])
    chart.add_data(data)
    chart.add_data(avgs)
    return chart.get_url()

  def chart_users_by_volume(self, context):
    """Pie chart showing users by volume.

    Syntax:
      {% chart users_by_volume width height %}
    """
    raise ChartUnavailableError, "not implemented"

class QueryNode(Node):
  def __init__(self, var_name, queryset, limit):
    self._queryset = queryset
    self._var_name = var_name
    self._limit_items = limit

  def render(self, context):
    context[self._var_name] = list(self._queryset[:self._limit_items])
    return ''

def user_stats(parser, token):
  """ {% user_stats <user> as <context_var> %} """
  tokens = token.contents.split()
  if len(tokens) != 4:
    raise TemplateSyntaxError('%s requires 3 arguments' % (tokens[0],))

  return StatsNode(tokens[1], tokens[3], stats.UserStats)

class StatsNode(Node):
  def __init__(self, obj_name, var_name, stats_cls):
    self._obj_var = Variable(obj_name)
    self._var_name = var_name
    self._stats_cls = stats_cls

  def render(self, context):
    obj = self._obj_var.resolve(context)
    context[self._var_name] = self._stats_cls(obj)
    return ''

register.tag('user_stats', user_stats)

def keg_stats(parser, token):
  """ {% keg_stats <keg> as <context_var> %} """
  tokens = token.contents.split()
  if len(tokens) != 4:
    raise TemplateSyntaxError('%s requires 3 arguments' % (tokens[0],))

  return StatsNode(tokens[1], tokens[3], stats.KegStats)

register.tag('keg_stats', keg_stats)

### filters

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
