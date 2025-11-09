from django.shortcuts import render, get_object_or_404, redirect
from .models import FacultySettings, CourseApproval, DepartmentHeadApproval

def _is_logged_dean(request):
    return request.session.get("role") == "DEAN"

def dashboard(request):
    if not _is_logged_dean(request):
        return redirect("login")

    course_pending = CourseApproval.objects.filter(status='PENDING').count()
    head_pending = DepartmentHeadApproval.objects.filter(status='PENDING').count()
    return render(request, 'dean/dashboard.html', {
        'course_pending': course_pending,
        'head_pending': head_pending,
        'username': request.session.get("username"),
    })

def course_approvals(request):
    if not _is_logged_dean(request):
        return redirect("login")

    approvals = CourseApproval.objects.filter(status='PENDING')
    return render(request, 'dean/course_approvals.html', {'approvals': approvals})

def approve_course(request, pk):
    if not _is_logged_dean(request):
        return redirect("login")

    approval = get_object_or_404(CourseApproval, pk=pk)
    approval.status = 'APPROVED'
    approval.save()
    return redirect('dean:course_approvals')

def faculty_settings(request):
    if not _is_logged_dean(request):
        return redirect("login")

    settings = FacultySettings.objects.get(faculty=request.session.get("username"))
    if request.method == "POST":
        settings.max_students_per_class = request.POST.get('max_students')
        settings.max_courses_per_student = request.POST.get('max_courses')
        settings.save()
    return render(request, 'dean/faculty_settings.html', {'settings': settings})
