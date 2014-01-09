from django.http import Http404

from registration.views import RegistrationView as BaseRegistrationView
from registration.backends.simple.views import RegistrationView as SimpleRegistrationView
from registration.backends.default.views import RegistrationView as DefaultRegistrationView


class RegistrationView(BaseRegistrationView):
    def __init__(self):
        self._simple = SimpleRegistrationView()
        self._default = DefaultRegistrationView()

    def _get_view(self, request):
        settings = request.kbsite.settings
        if not settings.registration_allowed:
            raise Http404('Registration is disabled.')
        if settings.registration_confirmation:
            return self._default
        else:
            return self._simple

    def get_success_url(self, request, user):
        return 'kb-account-main'

    def registration_allowed(self, request):
        settings = request.kbsite.settings
        return settings.registration_allowed

    def register(self, request, **cleaned_data):
        return self._get_view(request).register(request, **cleaned_data)
