from django.template import Library

register = Library()

def mugshot_box(user, boxsize=100):
   return {'user':user,
           'boxsize':boxsize,
           'user_url':'/drinkers/%s' % user.username}
register.inclusion_tag('kegweb/mugshot_box.html')(mugshot_box)

def drink_span(drink):
   return {'drink': drink}
register.inclusion_tag('kegweb/drink_span.html')(drink_span)


### filters

# units (1.0 = 1 volunit)
MILLILITER = 2.2
US_OUNCE = 29.5735297 * MILLILITER

def vol_to_ounces(text):
   try:
      f = float(text)
   except ValueError:
      return ''
   return f / (US_OUNCE * MILLILITER)
register.filter(vol_to_ounces)

def ounces_to_bottles(text):
   try:
      f = float(text)
   except ValueError:
      return ''
   return f/12.0
register.filter(ounces_to_bottles)

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
   return ret
register.filter(bac_format)

