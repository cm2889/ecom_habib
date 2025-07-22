from functools import wraps
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def admin_required(view_func):
    """
    Decorator to check if the user is logged in and is an admin.
    If not authenticated, redirects to login page.
    If authenticated but not admin, redirects to login page.
    """
    @login_required(login_url='backend:backend_login')
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_superuser or getattr(request.user, 'admin', False):
            return view_func(request, *args, **kwargs)
        return redirect('backend:backend_login')
    return _wrapped_view
