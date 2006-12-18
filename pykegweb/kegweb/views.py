from django.views.generic.list_detail import object_detail, object_list
from django.views.generic.simple import direct_to_template, redirect_to
from django.shortcuts import render_to_response
from django.http import Http404

from pykegweb.kegweb.models import *

# TODO: figure out how to get the appname (places that reference 'kegweb') and
# use that instead

def default_context():
   c = {}
   c['top_5'] = KegbotUser.objects.all()[:5]
   c['boxsize'] = 100
   return c

### main page

def index(request):
   context = default_context()
   context['last_drinks'] = Drink.objects.filter(status='valid').order_by('-endtime')[:5]
   context['template'] = 'index.html'
   return render_to_response('index.html', context)
   #return direct_to_template(request, 'index.html', extra_context=context)

### object lists and detail (generic views)

def user_list(request):
   user_list = KegbotUser.objects.all()
   return object_list(request, queryset=user_list, template_object_name='drinker',
         template_name='kegweb/drinker_list.html', extra_context=default_context())

def user_detail(request, username=None, user_id=None):
   extra = default_context()
   params = {
      'extra_context': extra,
      'template_object_name': 'drinker',
      'template_name': 'kegweb/drinker_detail.html',
   }

   if username:
      user_list = KegbotUser.objects.filter(username__exact=username)
      params['slug'] = username
      params['slug_field'] = 'username'
   elif user_id:
      user_list = KegbotUser.objects.filter(id__exact=user_id)
      params['object_id'] = user_id
      if user_list:
         return redirect_to(request, url='/drinker/'+user_list[0].username)
   else:
      raise Http404

   drinks = Drink.objects.filter(user__exact=user_list[0]).order_by('-starttime')
   extra['binges'] = Binge.objects.filter(user__exact=user_list[0])
   extra['drinks'] = drinks

   # TODO: fix or remove; broken in kegbotweb
   extra['rating'] = 'standard'
   extra['avg_drinks_hour'] = 0.0

   # TODO: this feels very wrong...
   extra['first_drink'] = drinks[0]
   extra['last_drink'] = drinks[drinks.count()-1]

   extra['total_volume'] = 0.0

   params['queryset'] = user_list
   params['extra_context'] = extra
   return object_detail(request, **params)

def keg_list(request):
   keg_list = Keg.objects.all()
   return object_list(request, queryset=keg_list, template_object_name='keg',
         extra_context=default_context())

def keg_detail(request, keg_id):
   keg_list = Keg.objects.filter(id__exact=keg_id)
   extra = default_context()
   extra.update({
      # TODO FIXME - no nice way to deal with null results
      'prev_keg': Keg.objects.filter(id__lt=keg_id),
      'next_keg': Keg.objects.filter(id__gt=keg_id),
      'last_pour': Drink.objects.filter(keg__exact=keg_id)[0],
   })

   # load all drinks this keg (for full drink listing block)
   extra['drinks'] = Drink.objects.filter(keg__exact=keg_id)

   # drinking groups
   # basic idea:
   #  - iterate through all binges that fall on this keg
   #  - group binges that overlap in time
   #  - reduce each group to a list of unique members, plus date extents
   # TODO: optimize the binges select
   binges = Binge.objects.all()
   groups, current_group = [], []
   for binge in binges:
      if not current_group:
         current_group = [binge]
      elif binge.starttime <= current_group[-1].endtime:
         current_group.append(binge)
      else:
         groups.append(current_group)
         current_group = []
   if current_group:
      groups.append(current_group)

   reduced_groups = []
   for group in groups:
      totalvol = 0.0
      users = {}
      if len(group) < 2:
         continue
      for binge in group:
         users[binge.user.username] = binge.user
         totalvol += binge.volume
      reduced_groups.append({
            'start':    group[0].starttime,
            'end':      group[-1].endtime,
            'drinkers': users.values(),
            'totalvol': totalvol,
      })

   extra['drinking_groups'] = reduced_groups

   return object_detail(request, queryset=keg_list, object_id=keg_id,
         template_object_name='keg', extra_context=extra)

def drink_list(request):
   drink_list = Drink.objects.all()
   return object_list(request, queryset=drink_list, template_object_name='drink',
         extra_context=default_context())

def drink_detail(request, drink_id):
   drink_list = Drink.objects.filter(id__exact=drink_id)
   extra = default_context()

   # fetch any binges happening at the same time ("drinking with" feature)
   # TODO: figure out the right way to reference drink_list[0]
   concurrent_binges = Binge.objects.filter(starttime__lte=drink_list[0].endtime,
         endtime__gte=drink_list[0].starttime)
   concurrent_binges = concurrent_binges.exclude(
         user__exact=drink_list[0].user)
   extra['concurrent_binges'] = concurrent_binges

   # fetch the current binge, if it exists
   # TODO: i used to do this by selecting for (startdrink.id >= drink.id &&
   # enddrink.id <= drink.id), but django doesn't let me use the id values in
   # the statement.. figure out if there is some other way to do that..
   binges = Binge.objects.filter(starttime__lte=drink_list[0].endtime,
         endtime__gte=drink_list[0].starttime,
         user__exact=drink_list[0].user)
   if binges:
      extra['binge'] = binges[0]

   return object_detail(request, queryset=drink_list, object_id=drink_id,
         template_object_name='drink', extra_context=extra)

