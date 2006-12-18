from django import template

register = template.Library()

def mugshot_box(user, boxsize=100):
   return {'user':user,
           'boxsize':boxsize,
           'user_url':'/drinkers/%s' % user.username}
register.inclusion_tag('boxes/mugshot.html')(mugshot_box)

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
