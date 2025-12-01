# students/views.py
from django.shortcuts import render, get_object_or_404
from accounts.decorators import require_role
from .models import Student
from courses.models import CourseEnrollment
from accounts.models import SimpleUser
from django.shortcuts import redirect

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
        student = Student.objects.filter(user=simple_user).first()
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

def dashboard_redirect(request):
    return redirect('students:dashboard')

@require_role("STUDENT")
def profile(request):
    """Öğrenci profili"""
    username = request.session.get("username")
    
    if not username:
        return render(request, "students/profile.html", {'student': None})
    
    try:
        simple_user = SimpleUser.objects.get(username=username)
        student = Student.objects.filter(user=simple_user).first()
        
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
        student = Student.objects.filter(user=simple_user).first()

    except (SimpleUser.DoesNotExist, Student.DoesNotExist):
        student = None

    # Eğer öğrenci bulunduysa ilgili ders, not ve component bilgilerini çek
    enrollments = None
    if student:
        enrollments = (
            student.course_enrollments
            .select_related("course")
            .prefetch_related(
                "grades__component"     # Grade içindeki component bilgilerini getirir
            )
        )

    context = {
        'student': student,
        'enrollments': enrollments,
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
        student = Student.objects.filter(user=simple_user).first()
        
    except (SimpleUser.DoesNotExist, Student.DoesNotExist):
        student = None
    
    context = {
        'student': student,
    }
    return render(request, 'students/attendance.html', context)

@require_role("ADMIN")
def admin_student_profile(request, student_id):
    """Admin panelinden öğrenci profili görüntüleme"""

    # Student modelinde student_no alanı var, ona göre buluyoruz
    student = get_object_or_404(Student, student_no=student_id)

    context = {
        "student": student,
    }
    return render(request, "students/admin_student_profile.html", context)
