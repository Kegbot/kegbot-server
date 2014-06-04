# Copyright 2014 Bevbot LLC, All Rights Reserved
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

import pytz

from django.conf import settings
from django.core.urlresolvers import reverse
from django.template import Library
from django.template import Node
from django.template import VariableDoesNotExist
from django.template import TemplateSyntaxError
from django.template import Variable
from django.template.defaultfilters import pluralize
from django.utils import timezone
from django.utils.safestring import mark_safe

from kegbot.util import kbjson
from kegbot.util import units
from kegbot.util import util

from pykeg.core import models
from pykeg.web.charts import charts

register = Library()


@register.inclusion_tag('kegweb/mugshot_box.html', takes_context=True)
def mugshot_box(context, user, boxsize=0):
    return {
        'user': user,
        'boxsize': boxsize,
        'guest_info': context.get('guest_info', None),
        'STATIC_URL': context.get('STATIC_URL')
    }


@register.inclusion_tag('kegweb/picture-gallery.html')
def gallery(picture_or_pictures, thumb_size='span2', gallery_id=''):
    c = {}
    if not hasattr(picture_or_pictures, '__iter__'):
        c['gallery_pictures'] = [picture_or_pictures]
    else:
        c['gallery_pictures'] = picture_or_pictures
    c['thumb_size'] = thumb_size
    c['gallery_id'] = gallery_id
    return c


@register.inclusion_tag('kegweb/badge.html')
def badge(amount, caption, style='', is_volume=False, do_pluralize=False):
    if is_volume:
        amount = mark_safe(VolumeNode.format(amount, 'mL'))
    if do_pluralize:
        caption += pluralize(amount)
    return {
        'badge_amount': amount,
        'badge_caption': caption,
        'badge_style': style,
    }


@register.inclusion_tag('kegweb/includes/progress_bar.html')
def progress_bar(progress_int, extra_css=''):
    c = {}
    try:
        progress_int = max(int(progress_int), 0)
    except ValueError:
        progress_int = 0
    progress_int = min(progress_int, 100)

    c['progress_int'] = progress_int
    c['extra_css'] = extra_css
    if progress_int < 10:
        bar_type = 'bar-danger'
    elif progress_int < 25:
        bar_type = 'bar-warning'
    else:
        bar_type = 'bar-success'
    c['bar_type'] = bar_type
    return c


### navitem

@register.tag('navitem')
def navitem(parser, token):
    """{% navitem <viewname> <title> [exact] %}"""
    tokens = token.split_contents()
    if len(tokens) < 3:
        raise TemplateSyntaxError('%s requires at least 3 tokens' % tokens[0])
    return NavitemNode(*tokens[1:])


class NavitemNode(Node):
    def __init__(self, *args):
        self._viewname = args[0]
        self._title = args[1]
        self._exact = 'exact' in args[2:]

    def render(self, context):
        viewname = Variable(self._viewname).resolve(context)
        title = Variable(self._title).resolve(context)
        if viewname.startswith('/'):
            urlbase = viewname
        else:
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
        raise TemplateSyntaxError('%s requires 2 tokens' % tokens[0])
    return TimeagoNode(tokens[1])


class TimeagoNode(Node):
    def __init__(self, timestamp_varname):
        self._timestamp_varname = timestamp_varname

    def render(self, context):
        tv = Variable(self._timestamp_varname)
        ts = tv.resolve(context)

        # Try to set time zone information.
        if settings.TIME_ZONE and not settings.USE_TZ:
            try:
                tz = pytz.timezone(settings.TIME_ZONE)
                ts = tz.localize(ts)
            except pytz.UnknownTimeZoneError:
                pass

        iso = ts.isoformat()
        alt = timezone.localtime(ts).strftime("%A, %B %d, %Y %I:%M%p")
        return '<abbr class="timeago" title="%s">%s</abbr>' % (iso, alt)


### temperature

@register.tag('temperature')
def temperature_tag(parser, token):
    """{% temperature <temp_c> %}"""
    tokens = token.contents.split()
    if len(tokens) < 2:
        raise TemplateSyntaxError('%s requires at least 2 tokens' % tokens[0])
    return TemperatureNode(tokens[1])


class TemperatureNode(Node):
    TEMPLATE = "%(amount)s&deg; %(unit)s"

    def __init__(self, varname):
        self.varname = varname

    def render(self, context):
        v = Variable(self.varname)
        try:
            amount = v.resolve(context)
        except (VariableDoesNotExist, ValueError):
            raise
            amount = 'unknown'

        unit = 'C'
        kbsite = models.KegbotSite.get()
        if kbsite.temperature_display_units == 'f':
            unit = 'F'
            amount = util.CtoF(amount)

        return self.TEMPLATE % {'amount': amount, 'unit': unit}

### volume


@register.tag('volume')
def volumetag(parser, token):
    """{% volume <amount> %}"""
    tokens = token.contents.split()
    if len(tokens) < 2:
        raise TemplateSyntaxError('%s requires at least 2 tokens' % tokens[0])
    return VolumeNode(tokens[1], tokens[2:])


class VolumeNode(Node):
    TEMPLATE = """
      <span class="hmeasure %(extra_css)s" title="%(title)s">
        <span class="num">%(amount)s</span>
        <span class="unit">%(units)s</span>
      </span>""".strip()

    def __init__(self, volume_varname, extra_args):
        self._volume_varname = volume_varname
        self._extra_args = extra_args

    def render(self, context):
        tv = Variable(self._volume_varname)
        try:
            num = float(tv.resolve(context))
        except (VariableDoesNotExist, ValueError):
            num = 'unknown'
        unit = 'mL'
        make_badge = 'badge' in self._extra_args
        return self.format(num, unit, make_badge)

    @classmethod
    def format(cls, amount, units, make_badge=False):
        if amount < 0:
            amount = 0
        ctx = {
            'units': units,
            'amount': amount,
            'title': '%s %s' % (amount, units),
            'extra_css': 'badge ' if make_badge else '',
        }
        return cls.TEMPLATE % ctx

### drinker


@register.tag('drinker_name')
def drinker_name_tag(parser, token):
    """{% drinker_name <drink_or_user_obj> [nolink] %}"""
    tokens = token.contents.split()
    if len(tokens) < 2:
        raise TemplateSyntaxError('%s requires at least 2 tokens' % tokens[0])
    return DrinkerNameNode(tokens[1], tokens[2:])


class DrinkerNameNode(Node):
    def __init__(self, drink_varname, extra_args):
        self._varname = drink_varname
        self._extra_args = extra_args

    def render(self, context):
        obj = Variable(self._varname)
        try:
            obj = obj.resolve(context)
        except (VariableDoesNotExist, ValueError):
            obj = None

        user = None
        if obj:
            if isinstance(obj, models.Drink) or isinstance(obj, models.SystemEvent):
                user = obj.user
            elif isinstance(obj, models.User):
                user = obj
        if user:
            if 'nolink' in self._extra_args:
                return user.get_full_name()
            else:
                return '<a href="%s">%s</a>' % (reverse('kb-drinker', args=[user.username]), user.get_full_name())
        return context['guest_info']['name']


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

        self._chart_fn = getattr(charts, 'chart_%s' % (self._charttype,), None)

    def _get_chart_id(self, context):
        # TODO(mikey): Is there a better way to store _CHART_ID?
        if not hasattr(context, '_CHART_ID'):
            context._CHART_ID = 0
        context._CHART_ID += 1
        return context._CHART_ID

    def show_error(self, error_str):
        ctx = {
            'error_str': error_str,
            'chart_id': 0,
            'width': self._width,
            'height': self._height,
        }
        return ChartNode.ERROR_TMPL % ctx

    def render(self, context):
        if not self._chart_fn:
            return self.show_error("Unknown chart type: %s" % self._charttype)

        chart_id = self._get_chart_id(context)
        obj = Variable(self._args[0]).resolve(context)

        metric_volumes = context.get('metric_volumes', False)
        temperature_units = context.get('temperature_display_units', 'f')

        try:
            chart_result = self._chart_fn(obj, metric_volumes=metric_volumes,
                temperature_units=temperature_units)
        except charts.ChartError, e:
            return self.show_error(str(e))

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
            elif isinstance(v, dict):
                chart_data[k].update(v)
            else:
                chart_data[k] = v
        chart_data = kbjson.dumps(chart_data, indent=None)

        ctx = {
            'chart_id': chart_id,
            'width': self._width,
            'height': self._height,
            'chart_data': chart_data,
        }

        return ChartNode.CHART_TMPL % ctx


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
        raise TemplateSyntaxError('Unknown volume format: %s' % fmt)
    return float(res)
