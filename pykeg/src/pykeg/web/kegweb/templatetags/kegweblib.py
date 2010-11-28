import datetime

from django.core import urlresolvers
from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Variable
from django.utils.safestring import mark_safe

from pykeg.core import kbjson
from pykeg.core import models
from pykeg.core import units

class KegweblibError(Exception):
  """Base kegweblib execption."""

class ChartUnavailableError(KegweblibError):
  """Thrown when a chart cannot be rendered."""

register = Library()

def to_pints(volume):
  return float(units.Quantity(volume).ConvertTo.Pint)

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


### timeago

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


### chart

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
  next_chart_id = 0
  def __init__(self, charttype, width, height, args):
    self._charttype = charttype
    self._width = width
    self._height = height
    self._args = args

    try:
      self._chart_fn = getattr(self, 'chart_%s' % (self._charttype,))
    except AttributeError:
      raise TemplateSyntaxError('unknown chart type: %s' % self._charttype)

  def render(self, context):
    chart_id = str(ChartNode.next_chart_id)
    ChartNode.next_chart_id += 1

    width = self._width
    height = self._height

    TMPL = '''
    <!-- begin chart %(chart_id)s -->
    <div id="chart-%(chart_id)s-container"
      style="height: %(height)spx; width: %(width)spx; margin-top:5px;"></div>
    <script type="text/javascript">
      var chart_%(chart_id)s;
      $(document).ready(function() {
        var chart_data = %(chart_data)s;
        chart_%(chart_id)s = new Highcharts.Chart(chart_data);
      });
    </script>
    <!-- end chart %(chart_id)s -->

    '''

    chart_base = {
      'chart': {
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

    chart_data = self._chart_fn(context)
    for k, v in chart_base.iteritems():
      if k not in chart_data:
        chart_data[k] = v
      elif type(v) == type({}):
        chart_data[k].update(v)
      else:
        chart_data[k] = v
    chart_data = kbjson.dumps(chart_data)
    return TMPL % vars()

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

    hours = 6
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

    res = {
      'series': [
        {
          'data': temps,
          'marker': {
            'enabled': False,
          },
        },
      ],
      'tooltip': {
        'enabled': False,
      },
      'xAxis': {
        'categories': ['Temperature'],
        'labels': {
          'enabled': False,
        },
        'tickInterval': 0,
      },
      'yAxis': {
        'labels': {
          'enabled': False,
        },
        'tickInterval': 1,
      },
    }
    return res

  def chart_keg_volume(self, context):
    """ Shows a horizontal bar chart of keg served/remaining volume.

    Syntax:
      {% chart keg_volume <keg> width height %}
    Args:
      keg - the keg instance to chart
    """
    keg, stats = self._get_obj_stats(context)

    served = units.Quantity(stats.get('total_volume', 0.0))
    served_pints = to_pints(served)
    full_pints = to_pints(keg.full_volume())
    remain_pints = full_pints - served_pints

    res = {
      'chart': {
        'defaultSeriesType': 'bar',
      },
      'series': [
        {'data': [served_pints]},
      ],
      'tooltip': {
        'enabled': False,
      },
      'xAxis': {
        'categories': ['Served'],
        'labels': {
          'enabled': False,
        },
        'gridLineWidth': 0,
      },
      'yAxis': {
        'endOnTick': False,
        'min': 0,
        'max': full_pints,
        'lineWidth': 0,
        'labels': {
          'enabled': False,
        },
      },
    }
    return res

  def chart_volume_by_day(self, context):
    """ Shows a horizontal bar chart of keg served/remaining volume.

    Syntax:
      {% chart volume_by_day <keg> width height %}
    Args:
      obj - the keg or drinking session instance to chart
    """
    obj, stats = self._get_obj_stats(context)

    volmap = stats.get('volume_by_day_of_week')
    if not volmap:
      raise ChartUnavailableError, "Daily volumes unavailable"

    vals = []
    for k in sorted(volmap.keys()):
      vals.append(to_pints(volmap[k]))
    if len(vals) != 7:
      raise ChartUnavailableError, "Volume data is corrupt"
    return self._day_of_week_chart(vals)

  def chart_sessions_weekday(self, context):
    """ Vertical bar chart showing session volume by day of week.

    Syntax:
      {% chart sessions_weekday <user> width height %}
    Args:
      sessions - an iterable of DrinkingSession or UserDrinkingSessionPart
                 instances
    """
    user_var = Variable(self._args[0])
    user = user_var.resolve(context)
    if not user:
      raise ChartUnavailableError, "Must give a user as argument"
    chunks = user.user_session_chunks.all()

    weekdays = [0] * 7

    for chunk in chunks:
      weekday = chunk.starttime.weekday()
      weekdays[weekday] += to_pints(chunk.Volume())
    return self._day_of_week_chart(weekdays)

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

    buckets = [0]*6  # 1 or less, 2, 3, 4, 5, 6+
    labels = [
      '0-1',
      '2',
      '3',
      '4',
      '5',
      '6+'
    ]
    for sess in sessions:
      pints = to_pints(sess.Volume())
      intval = int(pints)
      if intval <= 1:
        buckets[0] += 1
      elif intval >= 6:
        buckets[-1] += 1
      else:
        buckets[intval - 1] += 1

    res = {
      'xAxis': {
        'categories': labels,
      },
      'series': [
        {'data': buckets},
      ],
      'yAxis': {
        'min': 0,
      },
      'chart': {
        'defaultSeriesType': 'column',
      }
    }
    return res

  def chart_users_by_volume(self, context):
    """Pie chart showing users by volume.

    Syntax:
      {% chart users_by_volume obj width height %}
    Args:
      obj - the keg or drinking session instance to chart
    """
    obj, stats = self._get_obj_stats(context)
    volmap = stats.get('volume_by_drinker', {})
    if not volmap:
      raise ChartUnavailableError, "no data"

    data = []
    for username, volume_ml in volmap.iteritems():
      pints = to_pints(volume_ml)
      label = '<b>%s</b> (%.1f)' % (username, pints)
      data.append((label, pints))

    other_vol = 0
    for volume_ml, username in data[10:]:
      other_vol += volume_ml
    data = data[:10]

    if other_vol:
      data.append('all others', to_pints(other_vol))

    def my_sort(a, b):
      return cmp(a[1], b[1])
    data.sort(my_sort)

    res = {
      'series': [
        {
          'type': 'pie',
          'name': 'Drinkers by Volume',
          'data': data,
        }
      ],
      'yAxis': {
        'min': 0,
      },
      'chart': {
        'defaultSeriesType': 'column',
      },
      'tooltip': {
        'enabled': False,
      },
    }
    return res

  def _day_of_week_chart(self, vals):
    labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']

    # convert from 0=Monday to 0=Sunday
    vals.insert(0, vals.pop(-1))

    res = {
      'xAxis': {
        'categories': labels,
      },
      'yAxis': {
        'min': 0,
      },
      'series': [
        {'data': vals},
      ],
      'tooltip': {
        'enabled': False,
      },
      'chart': {
        'defaultSeriesType': 'column',
      }
    }
    return res

  def _get_obj_stats(self, context):
    obj_var = Variable(self._args[0])
    obj = obj_var.resolve(context)

    if not hasattr(obj, 'GetStats'):
      raise ChartUnavailableError, "Argument does not support stats"

    stats = obj.GetStats()
    if not stats:
      raise ChartUnavailableError, "Stats unavailable"
    return obj, stats

@register.filter
def volume(text, fmt='pints'):
  vol = units.Quantity(float(text))
  if fmt == 'pints':
    res = vol.ConvertTo.Pint
  elif fmt == 'liters':
    res = vol.ConvertTo.Liter
  elif fmt == 'ounces':
    res = vol.ConvertTo.Ounce
  elif fmt == 'gallons':
    res = vol.ConvertTo.USGallon
  elif fmt == 'twelveounces':
    res = vol.ConvertTo.TwelveOunceBeer
  elif fmt == 'halfbarrels':
    res = vol.ConvertTo.HalfBarrelKeg
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
