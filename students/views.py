from django.shortcuts import render
from accounts.decorators import require_role

@require_role("STUDENT")
def dashboard(request):
    return render(request, "students/dashboard.html")

