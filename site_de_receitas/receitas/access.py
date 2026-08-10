from functools import wraps

from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse


def superuser_required(view_func):
    """Restrict a view to authenticated superusers."""

    @wraps(view_func)
    def wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect(f"{reverse('membros')}?auth=login")
        if not request.user.is_superuser:
            raise PermissionDenied("Esta área é restrita a superusuários.")
        return view_func(request, *args, **kwargs)

    return wrapped_view
