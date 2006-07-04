from django import template

register = template.Library()

def mugshot_box(user, boxsize=100):
   return {'user':user,
           'boxsize':boxsize,
           'user_url':'/drinker/%s' % user.username}
register.inclusion_tag('boxes/mugshot.html')(mugshot_box)


