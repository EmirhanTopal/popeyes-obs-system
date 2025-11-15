# students/views.py
from django.shortcuts import render, get_object_or_404
from accounts.decorators import require_role
from .models import Student
from accounts.models import SimpleUser

@require_role("STUDENT")
def dashboard(request):
    """Öğrenci dashboard - Session'dan Student bul"""
    username = request.session.get("username")
    
    if not username:
        return render(request, "students/dashboard.html", {'student': None})
    
    try:
        # SimpleUser'dan Student'e geçiş
        simple_user = SimpleUser.objects.get(username=username)
        
        # Student'i bul (full_name veya email ile)
        student = Student.objects.filter(
            full_name=simple_user.get_full_name()
        ).first()
        
        # Eğer bulamazsak email ile dene
        if not student and simple_user.email:
            student = Student.objects.filter(email=simple_user.email).first()
            
    except (SimpleUser.DoesNotExist, Student.DoesNotExist):
        student = None
    
    context = {
        'student': student,
        'username': username,
    }
    return render(request, "students/dashboard.html", context)

@require_role("STUDENT")
def profile(request):
    """Öğrenci profili"""
    username = request.session.get("username")
    
    if not username:
        return render(request, "students/profile.html", {'student': None})
    
    try:
        simple_user = SimpleUser.objects.get(username=username)
        student = Student.objects.filter(
            full_name=simple_user.get_full_name()
        ).first()
        
        if not student and simple_user.email:
            student = Student.objects.filter(email=simple_user.email).first()
            
    except (SimpleUser.DoesNotExist, Student.DoesNotExist):
        student = None
    
    context = {
        'student': student,
    }
    return render(request, 'students/profile.html', context)

@require_role("STUDENT")
def courses(request):
    """Öğrencinin dersleri"""
    username = request.session.get("username")
    
    if not username:
        return render(request, "students/courses.html", {'student': None})
    
    try:
        simple_user = SimpleUser.objects.get(username=username)
        student = Student.objects.filter(
            full_name=simple_user.get_full_name()
        ).first()
        
    except (SimpleUser.DoesNotExist, Student.DoesNotExist):
        student = None
    
    context = {
        'student': student,
    }
    return render(request, 'students/courses.html', context)

@require_role("STUDENT")
def attendance(request):
    """Öğrenci devamsızlık bilgisi"""
    username = request.session.get("username")
    
    if not username:
        return render(request, "students/attendance.html", {'student': None})
    
    try:
        simple_user = SimpleUser.objects.get(username=username)
        student = Student.objects.filter(
            full_name=simple_user.get_full_name()
        ).first()
        
    except (SimpleUser.DoesNotExist, Student.DoesNotExist):
        student = None
    
    context = {
        'student': student,
    }
    return render(request, 'students/attendance.html', context)