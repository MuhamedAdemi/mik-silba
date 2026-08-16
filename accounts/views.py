from django.contrib.auth.views import LoginView, LogoutView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.views.decorators.http import require_POST

from config.translations import LANGUAGES

from .forms import StyledAuthenticationForm


class StaffLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class StaffLogoutView(LogoutView):
    pass


@require_POST
def set_language(request, code):
    valid_codes = {c for c, _ in LANGUAGES}
    if code in valid_codes:
        request.session["lang"] = code
    next_url = request.POST.get("next") or request.META.get("HTTP_REFERER") or reverse("venue:table_grid")
    return HttpResponseRedirect(next_url)
