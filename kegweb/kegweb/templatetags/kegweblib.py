import time

from django.template import Library
from django.template import Node
from django.template import TemplateSyntaxError
from django.template import Variable
from django.utils.safestring import mark_safe

from pykeg.core import models
from pykeg.core import units

from kegweb.kegweb import stats

register = Library()

def mugshot_box(user, boxsize=100):
   q = models.UserPicture.objects.filter(user=user.id)
   img_url = '/site_media/images/unknown-drinker.png'
   if len(q):
     pic = q[0]
     img_url = pic.image.url

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

# http://www.djangosnippets.org/snippets/412/
@register.filter
def humanizeTimeDiff(timestamp = None):
    """
    Returns a humanized string representing time difference
    between now() and the input timestamp.

    The output rounds up to days, hours, minutes, or seconds.
    4 days 5 hours returns '4 days'
    0 days 4 hours 3 minutes returns '4 hours', etc...
    """
    import datetime

    timeDiff = datetime.datetime.now() - timestamp
    days = timeDiff.days
    hours = timeDiff.seconds/3600
    minutes = timeDiff.seconds%3600/60
    seconds = timeDiff.seconds%3600%60

    str = ""
    tStr = ""
    if days > 7:
        return timestamp.strftime("%a %b %d %y %H:%M")
    if days > 0:
        if days == 1:   tStr = "day"
        else:           tStr = "days"
        str = str + "%s %s ago" %(days, tStr)
        return str
    elif hours > 0:
        if hours == 1:  tStr = "hour"
        else:           tStr = "hours"
        str = str + "%s %s ago" %(hours, tStr)
        return str
    elif minutes > 0:
        if minutes == 1:tStr = "min"
        else:           tStr = "mins"
        str = str + "%s %s ago" %(minutes, tStr)
        return str
    elif seconds > 0:
        if seconds == 1:tStr = "sec"
        else:           tStr = "secs"
        str = str + "%s %s ago" %(seconds, tStr)
        return str
    else:
        return None
