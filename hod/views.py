from django.shortcuts import render
from accounts.decorators import require_role

@require_role("HOD")
def dashboard(request):
    return render(request, "hod/dashboard.html")
