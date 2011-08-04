from django.shortcuts import get_object_or_404
from pykeg.core import models

def kbsite_aware(f):
  def new_function(*args, **kwargs):
    if 'kbsite_name' in kwargs:
      kbsite_name = kwargs['kbsite_name']
      del kwargs['kbsite_name']
      if kbsite_name == '':
        kbsite_name = 'default'
      request = args[0]
      if not hasattr(request, 'kbsite'):
        request.kbsite = get_object_or_404(models.KegbotSite, name=kbsite_name)
    return f(*args, **kwargs)
  return new_function


