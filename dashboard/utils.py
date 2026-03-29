from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages

def dashboard_required(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("dashboard_login")
        if not (request.user.is_superuser or request.user.groups.filter(name__in=["Admin", "Staff"]).exists()):
            messages.error(request, "لا تملك صلاحية الدخول.")
            return redirect("dashboard_login")
        return view_func(request, *args, **kwargs)
    return _wrapped

def admin_only(view_func):
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect("dashboard_login")
        is_admin = request.user.is_superuser or request.user.groups.filter(name="Admin").exists()
        if not is_admin:
            messages.error(request, "هذه الصلاحية للمدير فقط.")
            return redirect("dashboard_home")
        return view_func(request, *args, **kwargs)
    return _wrapped