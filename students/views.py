# students/views.py
from django.shortcuts import render, get_object_or_404
from accounts.decorators import require_role
from .models import Student, StudentCourseEnrollment, CourseAttendance

@require_role("STUDENT")
def dashboard(request):
    """Öğrenci dashboard"""

    try:
        student = Student.objects.get(user=request.user)
    except Student.DoesNotExist:
        student = None
    
    context = {
        'student': student,
    }
    return render(request, "students/dashboard.html", context)

@require_role("STUDENT")
def profile(request):
    """Öğrenci profili - kendi profilini görüntüle"""
    student = get_object_or_404(Student, user=request.user)
    
    
    auto_courses = student.get_auto_courses()
    
    
    enrolled_courses = StudentCourseEnrollment.objects.filter(
        student=student.user, 
        is_active=True
    )
    
 
    attendance_records = CourseAttendance.objects.filter(student=student.user)
    
    context = {
        'student': student,
        'auto_courses': auto_courses,
        'enrolled_courses': enrolled_courses,
        'attendance_records': attendance_records,
    }
    return render(request, 'students/profile.html', context)

@require_role("STUDENT")
def courses(request):
    """Öğrencinin dersleri - kendi derslerini görüntüle"""
    student = get_object_or_404(Student, user=request.user)
    enrolled_courses = StudentCourseEnrollment.objects.filter(
        student=student.user, 
        is_active=True
    )
    
    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
    }
    return render(request, 'students/courses.html', context)

@require_role("STUDENT")
def attendance(request):
    """Öğrenci devamsızlık bilgisi - kendi devamsızlığını görüntüle"""
    student = get_object_or_404(Student, user=request.user)
    attendance_records = CourseAttendance.objects.filter(student=student.user)
    
    context = {
        'student': student,
        'attendance_records': attendance_records,
    }
    return render(request, 'students/attendance.html', context)

def admin_student_profile(request, student_id):
    """Admin için öğrenci profili görüntüleme"""
    student = get_object_or_404(Student, student_id=student_id)
    
    enrolled_courses = StudentCourseEnrollment.objects.filter(
        student=student.user, 
        is_active=True
    )
    attendance_records = CourseAttendance.objects.filter(student=student.user)
    
    context = {
        'student': student,
        'enrolled_courses': enrolled_courses,
        'attendance_records': attendance_records,
    }
    return render(request, 'students/admin_profile.html', context)