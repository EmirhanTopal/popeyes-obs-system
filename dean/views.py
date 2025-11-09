# dean/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import FacultySettings, CourseApproval, DepartmentHeadApproval

def is_dean(user):
    return hasattr(user, 'dean')  # sadece dekanlar erişsin

@login_required
@user_passes_test(is_dean)
def dashboard(request):
    course_pending = CourseApproval.objects.filter(status='PENDING').count()
    head_pending = DepartmentHeadApproval.objects.filter(status='PENDING').count()
    return render(request, 'dean/dashboard.html', {
        'course_pending': course_pending,
        'head_pending': head_pending,
    })

@login_required
@user_passes_test(is_dean)
def course_approvals(request):
    approvals = CourseApproval.objects.filter(status='PENDING')
    return render(request, 'dean/course_approvals.html', {'approvals': approvals})

@login_required
@user_passes_test(is_dean)
def approve_course(request, pk):
    approval = get_object_or_404(CourseApproval, pk=pk)
    approval.status = 'APPROVED'
    approval.approved_by = request.user.dean
    approval.save()
    return redirect('dean:course_approvals')

@login_required
@user_passes_test(is_dean)
def faculty_settings(request):
    settings = FacultySettings.objects.get(faculty=request.user.dean.faculty)
    if request.method == "POST":
        settings.max_students_per_class = request.POST.get('max_students')
        settings.max_courses_per_student = request.POST.get('max_courses')
        settings.save()
    return render(request, 'dean/faculty_settings.html', {'settings': settings})
