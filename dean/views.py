from django.shortcuts import render, get_object_or_404, redirect
from .models import FacultySettings, CourseApproval, DepartmentHeadApproval, Dean
from .forms import DepartmentForm
from departments.models import Department
from django.contrib import messages

def _is_logged_dean(request):
    return request.session.get("role") == "DEAN"

def dashboard(request):
    if not _is_logged_dean(request):
        return redirect("login")

    username = request.session.get("username")
    dean = Dean.objects.filter(user__username=username).select_related("faculty").first()

    if not dean:
        messages.error(request, "Bu kullanıcıya atanmış bir fakülte bulunamadı.")
        return redirect("login")

    # Bölüm formu — fakülteyi otomatik olarak dean'ın fakültesiyle dolduruyoruz
    dept_form = DepartmentForm()

    if request.method == "POST":
        dept_form = DepartmentForm(request.POST)
        if dept_form.is_valid():
            department = dept_form.save(commit=False)
            department.faculty = dean.faculty  # dean'ın fakültesine bağla
            department.save()
            messages.success(request, "Yeni bölüm başarıyla eklendi.")
            return redirect("dean:dashboard")
        else:
            messages.error(request, "Bölüm eklenemedi. Form hatalı.")

    departments = Department.objects.filter(faculty=dean.faculty)

    context = {
        "username": username,
        "faculty_name": dean.faculty.full_name,
        "dept_form": dept_form,
        "departments": departments,
    }
    return render(request, "dean/dashboard.html", context)
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
