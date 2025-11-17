from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from departments.models import Department, DepartmentCourse
from courses.models import Course
from teachers.models import Teacher
from students.models import Student
from .models import Dean, FacultySettings, DepartmentHeadApproval
from .forms import TeacherForm


def is_dean_logged(request):
    return request.session.get("role") == "DEAN"


def dashboard(request):
    if not is_dean_logged(request):
        return redirect("login")

    username = request.session.get("username")
    dean = Dean.objects.filter(user__username=username).select_related("faculty").first()

    if not dean:
        messages.error(request, "Dekan bulunamadı.")
        return redirect("login")

    departments = Department.objects.filter(faculty=dean.faculty)

    # HOD'nin oluşturduğu yeni dersler
    pending_courses = Course.objects.filter(
        status="PENDING",
        created_by_head__department__faculty=dean.faculty
    )

    # HOD'nin bölüme ders ekleme talepleri
    pending_department_courses = DepartmentCourse.objects.filter(
        approval_status="PENDING",
        department__faculty=dean.faculty
    )

    # HOD atama talepleri
    pending_heads = DepartmentHeadApproval.objects.filter(
        department__faculty=dean.faculty,
        status="PENDING"
    )

    selected_department_id = request.GET.get("dept")
    selected_department = None
    department_courses = None

    if selected_department_id:
        selected_department = Department.objects.filter(id=selected_department_id).first()
        department_courses = DepartmentCourse.objects.filter(department=selected_department)

    context = {
        "username": username,
        "dean": dean,
        "departments": departments,

        "pending_courses": pending_courses,                    # yeni dersler
        "pending_department_courses": pending_department_courses, # bölüme ders ekleme talepleri
        "pending_heads": pending_heads,

        "selected_department": selected_department,
        "department_courses": department_courses,
    }

    return render(request, "dean/dashboard.html", context)


# ================================
#  ONAY / RED
# ================================

def approve_course(request, pk):
    if not is_dean_logged(request):
        return redirect("login")

    course = get_object_or_404(Course, pk=pk)

    course.status = "APPROVED"
    course.save()

    DepartmentCourse.objects.create(
        department=course.created_by_head.department,
        course=course,
        semester=1,
        is_mandatory=True,
    )

    messages.success(request, f"{course.code} dersi onaylandı.")
    return redirect("dean:dashboard")


def reject_course(request, pk):
    if not is_dean_logged(request):
        return redirect("login")

    course = get_object_or_404(Course, pk=pk)
    course.status = "REJECTED"
    course.save()

    # Önkoşulları temizle
    course.prerequisites.clear()

    messages.warning(request, f"{course.code} dersi reddedildi.")
    return redirect("dean:dashboard")

def approve_department_course(request, pk):
    if not is_dean_logged(request):
        return redirect("login")

    dc = get_object_or_404(DepartmentCourse, pk=pk)

    dc.approval_status = "APPROVED"
    dc.save()

    messages.success(request, f"{dc.course.code} dersi {dc.department.name} bölümüne eklendi.")
    return redirect("dean:dashboard")


def reject_department_course(request, pk):
    if not is_dean_logged(request):
        return redirect("login")

    dc = get_object_or_404(DepartmentCourse, pk=pk)

    dc.approval_status = "REJECTED"
    dc.save()

    messages.warning(request, f"{dc.course.code} dersi bölüm ekleme talebi reddedildi.")
    return redirect("dean:dashboard")

# ================================
# ÖĞRETMEN EKLEME (AYRI SAYFA)
# ================================

def add_teacher(request):
    if not is_dean_logged(request):
        return redirect("login")

    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Öğretmen başarıyla eklendi.")
            return redirect("dean:add_teacher")
    else:
        form = TeacherForm()

    return render(request, "dean/add_teacher.html", {"form": form})

