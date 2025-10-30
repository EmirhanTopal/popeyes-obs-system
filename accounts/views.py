from django.shortcuts import render, redirect
from .models import SimpleUser

def login_view(request):
    role = request.session.get("role")
    if role:
        return _redirect_by_role(role)

    if request.method == "POST":
        username = (request.POST.get("username") or "").strip()
        password = request.POST.get("password") or ""

        user = SimpleUser.objects.filter(username=username, password=password).first()
        if user:
            request.session["username"] = user.username
            request.session["role"] = user.role
            return _redirect_by_role(user.role)
        return render(request, "auth/login.html", {"error": "Kullanıcı adı veya şifre hatalı."})

    return render(request, "auth/login.html")

def logout_view(request):
    request.session.flush()
    return redirect("login")

def _redirect_by_role(role):
    if role == "STUDENT": return redirect("/students/")
    if role == "TEACHER": return redirect("/teachers/")
    if role == "HOD":     return redirect("/hod/")
    if role == "DEAN":    return redirect("/dean/")
    return redirect("login")
