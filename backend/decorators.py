from functools import wraps
from django.shortcuts import redirect
from django.urls import reverse


def admin_required(view_func):
    """
    Decorator to check if the user is an admin.
    If not, redirect to the login page.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and (request.user.is_superuser or request.user.admin):
            return view_func(request, *args, **kwargs)
        return redirect(reverse('backend_login'))
    return _wrapped_view
