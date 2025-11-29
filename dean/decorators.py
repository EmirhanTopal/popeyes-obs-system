# dean/decorators.py
from django.shortcuts import redirect
from django.contrib import messages

def dean_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.session.get("role") != "DEAN":
            messages.error(request, "Bu sayfaya yalnızca dekan erişebilir.")
            return redirect("login")
        return view_func(request, *args, **kwargs)
    return wrapper
