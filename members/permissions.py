"""
Access-control helpers for the members app.

Two levels are used throughout the views:
  - admin_required: for administrator-only pages (staff users)
  - the student dashboard views instead find the member via
    request.user.member_profile - there is no way to reach another
    student's dashboard by guessing an ID, because the ID is never
    read from the URL or POST data for these views.
"""
from functools import wraps

from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied


def _is_admin(user):
    return user.is_authenticated and user.is_staff


def admin_required(view_func):
    """Only staff/admin users may pass. Anonymous users are redirected to login;
    authenticated non-staff users get a 403, not a login redirect (they ARE logged in,
    they just lack permission)."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)

    return _wrapped


def member_required(view_func):
    """Requires a logged-in user who has a MemberProfile attached."""

    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not hasattr(request.user, "member_profile"):
            raise PermissionDenied("No member profile is associated with this account.")
        return view_func(request, *args, **kwargs)

    return _wrapped
