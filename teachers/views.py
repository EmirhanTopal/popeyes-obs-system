from django.shortcuts import render
from accounts.decorators import require_role

@require_role("TEACHER")
def dashboard(request):
    return render(request, "teachers/dashboard.html")


