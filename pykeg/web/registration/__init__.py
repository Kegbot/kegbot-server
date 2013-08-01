from django.http import Http404

from registration.backends import default
from registration.backends import simple

_DEFAULT = default.DefaultBackend()
_SIMPLE = simple.SimpleBackend()

def get_real_backend(request):
    settings = request.kbsite.settings
    if not settings.registration_allowed:
        raise Http404('Registration is disabled.')
    if settings.registration_confirmation:
        return _DEFAULT
    else:
        return _SIMPLE

class KegbotRegistrationBackend:
    """Kegbot-aware backend which delegates to default backends."""
    def register(self, request, **kwargs):
        return get_real_backend(request).register(request, **kwargs)

    def activate(self, request, activation_key):
        return get_real_backend(request).activate(request, **kwargs)

    def registration_allowed(self, request):
        return request.kbsite.settings.registration_allowed

    def get_form_class(self, request):
        return get_real_backend(request).get_form_class(request)

    def post_registration_redirect(self, request, user):
        return ('/account/', (), {})

    def post_activation_redirect(self, request, user):
        return get_real_backend(request).post_activation_redirect(request, user)
