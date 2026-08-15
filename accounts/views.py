from django.contrib.auth.views import LoginView, LogoutView

from .forms import StyledAuthenticationForm


class StaffLoginView(LoginView):
    template_name = "accounts/login.html"
    authentication_form = StyledAuthenticationForm
    redirect_authenticated_user = True


class StaffLogoutView(LogoutView):
    pass
