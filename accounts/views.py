from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView, LogoutView
from django.db.models import ProtectedError
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from config.translations import LANGUAGES

from .decorators import admin_required
from .forms import StaffCreateForm, StyledAuthenticationForm


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


@admin_required
def staff_list(request):
    staff = User.objects.select_related("profile").order_by("-is_superuser", "profile__role", "username")
    return render(request, "accounts/staff_list.html", {"staff": staff})


@admin_required
def staff_create(request):
    allow_admin_role = request.user.is_superuser
    if request.method == "POST":
        form = StaffCreateForm(request.POST, allow_admin_role=allow_admin_role)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                password=form.cleaned_data["password"],
            )
            user.profile.role = form.cleaned_data["role"]
            user.profile.display_name = form.cleaned_data["display_name"]
            user.profile.save(update_fields=["role", "display_name"])
            messages.success(request, f"{user.username} u krijua.")
            return redirect("accounts:staff_list")
    else:
        form = StaffCreateForm(allow_admin_role=allow_admin_role)
    return render(request, "accounts/staff_form.html", {"form": form})


@admin_required
@require_POST
def staff_delete(request, user_id):
    target = get_object_or_404(User, pk=user_id)

    if target == request.user:
        messages.error(request, "S'mund ta fshish/çaktivizosh llogarinë tënde.")
        return redirect("accounts:staff_list")

    target_is_admin = target.is_superuser or (
        getattr(target, "profile", None) and target.profile.is_admin
    )
    if target_is_admin and not request.user.is_superuser:
        messages.error(request, "Vetëm superuser mund të fshijë/çaktivizojë llogari admin.")
        return redirect("accounts:staff_list")

    username = target.username
    try:
        target.delete()
        messages.success(request, f"{username} u fshi.")
    except ProtectedError:
        target.is_active = False
        target.save(update_fields=["is_active"])
        messages.warning(
            request,
            f"{username} ka histori porosish (stolove të mbyllura), kështu që nuk u fshi — "
            "u çaktivizua (nuk mund të kyçet më) por të dhënat e shitjeve u ruajtën.",
        )
    return redirect("accounts:staff_list")
