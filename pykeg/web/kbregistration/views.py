from django.contrib.auth import authenticate
from django.contrib.auth import login
from django.shortcuts import redirect
from django.shortcuts import render

from pykeg.web.kbregistration.forms import KegbotRegistrationForm
from pykeg.backend import get_kegbot_backend

from pykeg.core import models

"""Kegbot-aware registration views."""


def register(request):
    context = {}
    form = KegbotRegistrationForm()

    # Check if we need an invitation before processing the request further.
    invite = None
    if request.kbsite.registration_mode != "public":
        invite_code = None
        if "invite_code" in request.GET:
            invite_code = request.GET["invite_code"]
            request.session["invite_code"] = invite_code
        else:
            invite_code = request.session.get("invite_code", None)

        if not invite_code:
            r = render(request, "registration/invitation_required.html", context=context)
            r.status_code = 401
            return r

        try:
            invite = models.Invitation.objects.get(invite_code=invite_code)
        except models.Invitation.DoesNotExist:
            pass

        if not invite or invite.is_expired():
            r = render(request, "registration/invitation_expired.html", context=context)
            r.status_code = 401
            return r

    if request.method == "POST":
        form = KegbotRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"]
            password = form.cleaned_data.get("password1")

            backend = get_kegbot_backend()
            backend.create_new_user(username=username, email=email, password=password)

            if invite:
                invite.delete()
                if "invite_code" in request.session:
                    del request.session["invite_code"]

            if password:
                new_user = authenticate(username=username, password=password)
                login(request, new_user)
                return redirect("kb-account-main")

            return render(request, "registration/registration_complete.html", context=context)

    context["form"] = form
    return render(request, "registration/registration_form.html", context=context)
