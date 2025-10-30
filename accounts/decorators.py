from functools import wraps
from django.shortcuts import redirect

def require_role(expected_role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped(request, *args, **kwargs):
            role = request.session.get("role")
            if role != expected_role:
                return redirect("login")  # login’e gönder
            return view_func(request, *args, **kwargs)
        return _wrapped
    return decorator
