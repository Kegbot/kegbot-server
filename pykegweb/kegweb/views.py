# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from pykegweb.kegweb.models import *

def default_context():
   c = {}
   c['kegs'] = Keg.objects.all()[:5]
   c['top_5'] = User.objects.all()[:5]
   c['boxsize'] = 100
   c['kegweb'] = None
   return c

def index(request):
   c = default_context()
   c['last_drinks'] = Drink.objects.filter(status='valid').order_by('-endtime')[:5]
   return render_to_response('index.html', c)
   #return HttpResponse("Hello, world. You're at the keg index. %s" % kegs)

def kegindex(request):
   c = default_context()
   c['kegs'] = Keg.objects.all()
   return render_to_response('keg/index.html', c)
   #return HttpResponse("Hello, world. You're at the keg index. %s" % kegs)

def kegdetail(request, keg_id):
   return HttpResponse("Hello, world. You're at keg %s." % keg_id)
