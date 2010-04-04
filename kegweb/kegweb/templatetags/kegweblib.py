import datetime
import pygooglechart

from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Variable
from django.utils.safestring import mark_safe

from pykeg.core import models
from kegweb.kegweb import stats

register = Library()

def mugshot_box(user, boxsize=100):
  img_url = '/site_media/images/unknown-drinker.png'

  profile = user.get_profile()
  if profile:
    if profile.mugshot:
      img_url = profile.mugshot.image.url

  return {
      'user' : user,
      'boxsize' : boxsize,
      'user_url' : '/drinkers/%s' % user.username,
      'img_url': img_url,
  }
register.inclusion_tag('kegweb/mugshot_box.html')(mugshot_box)

def drink_span(drink):
  return {'drink' : drink}
register.inclusion_tag('kegweb/drink_span.html')(drink_span)

def show_drink_group(group):
  return {'group' : group}
register.inclusion_tag('kegweb/drink_group.html')(show_drink_group)

def render_page(page):
  return {'page' : page}
register.inclusion_tag('kegweb/page_block.html')(render_page)

def latest_drinks(parser, token):
  """ {% latest_drinks [number] as <context_var> %} """
  tokens = token.contents.split()
  if len(tokens) not in (3, 4):
    raise TemplateSyntaxError('%s requires 0, 1, or 3 arguments' % (tokens[0],))

  if len(tokens) > 3:
    num_items = tokens[1]
  else:
    num_items = 5

  if tokens[2] != 'as':
    raise TemplateSyntaxError('%s Argument 2 must be "as"' % (tokens[0],))

  var_name = tokens[3]
  queryset = models.Drink.objects.all().order_by('-starttime')

  return QueryNode(var_name, queryset, num_items)

register.tag('latest_drinks', latest_drinks)


def sensor_chart(parser, token):
  """{% sensor_chart <name> %}"""
  tokens = token.contents.split()
  if len(tokens) != 2:
    raise TemplateSyntaxError('%s requires 2 arguments' % (tokens[0],))

  return SensorChartNode(tokens[1])


class SensorChartNode(Node):
  def __init__(self, sensor_name):
    self._sensor_name_var = Variable(sensor_name)

  def render(self, context):
    sensor_name = self._sensor_name_var.resolve(context)
    try:
      sensor = models.ThermoSensor.objects.get(nice_name=sensor_name)
    except models.ThermoSensor.DoesNotExist:
      return ''

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
      return ''

    chart = pygooglechart.SparkLineChart(200, 20)
    chart.add_data(temps)
    chart.fill_solid(pygooglechart.Chart.BACKGROUND, '00000000')
    chart.set_colours(['4D89F9'])
    return chart.get_url()

register.tag('sensor_chart', sensor_chart)


def keg_volume_chart(parser, token):
  """{% keg_volume_chart <keg> %}"""
  tokens = token.contents.split()
  if len(tokens) != 2:
    raise TemplateSyntaxError('%s requires 2 arguments' % (tokens[0],))

  return KegVolumeChartNode(tokens[1])


class KegVolumeChartNode(Node):
  def __init__(self, keg_var):
    self._keg_var = Variable(keg_var)

  def render(self, context):
    keg = self._keg_var.resolve(context)
    if not keg or not isinstance(keg, models.Keg):
      return ''

    served = keg.served_volume()
    full = keg.full_volume()

    served_pints = served.ConvertTo.Pint
    full_pints = full.ConvertTo.Pint
    remain_pints = (full - served).ConvertTo.Pint

    chart = pygooglechart.StackedHorizontalBarChart(200, 28,
        x_range=(0, full_pints))
    chart.set_bar_width(20)
    chart.set_colours(['4D89F9','C6D9FD'])
    chart.add_data([min(served_pints, full_pints)])
    chart.add_data([full_pints])
    return chart.get_url()

register.tag('keg_volume_chart', keg_volume_chart)


def sessions_weekday_chart(parser, token):
  """{% sessions_weekday_chart sessions %}"""
  tokens = token.contents.split()
  if len(tokens) != 2:
    raise TemplateSyntaxError('%s requires 2 arguments' % (tokens[0],))

  return SessionsWeekdayChartNode(tokens[1])


class SessionsWeekdayChartNode(Node):
  def __init__(self, sessions_var):
    self._sessions_var = Variable(sessions_var)

  def render(self, context):
    sessions = self._sessions_var.resolve(context)
    if not sessions:
      return ''

    weekdays = [0] * 7

    for sess in sessions:
      date = int(sess.starttime.strftime('%w'))
      weekdays[date] += int(sess.Volume())

    chart = pygooglechart.StackedVerticalBarChart(200, 64)
    chart.set_bar_width(20)
    chart.set_colours(['4D89F9','C6D9FD'])
    chart.add_data(weekdays)
    labels = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
    chart.set_axis_labels('x', labels)
    return chart.get_url()

register.tag('sessions_weekday_chart', sessions_weekday_chart)


def sessions_volume_chart(parser, token):
  """{% sessions_volume_chart sessions %}"""
  tokens = token.contents.split()
  if len(tokens) != 2:
    raise TemplateSyntaxError('%s requires 2 arguments' % (tokens[0],))

  return SessionsVolumeChartNode(tokens[1])


class SessionsVolumeChartNode(Node):
  def __init__(self, sessions_var):
    self._sessions_var = Variable(sessions_var)

  def render(self, context):
    sessions = self._sessions_var.resolve(context)
    if not sessions:
      return ''

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

    chart = pygooglechart.SimpleLineChart(200, 64)
    chart.set_colours(['4D89F9','C6D9FD'])
    chart.add_data(data)
    chart.add_data(avgs)
    return chart.get_url()

register.tag('sessions_volume_chart', sessions_volume_chart)



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
