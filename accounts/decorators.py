from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied


def admin_required(view_func):
    """Only lets in users whose StaffProfile.role is ADMIN."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        profile = getattr(request.user, "profile", None)
        if not (profile and profile.is_admin):
            raise PermissionDenied("Vetëm admini ka qasje këtu.")
        return view_func(request, *args, **kwargs)

    return _wrapped
