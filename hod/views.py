from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import SimpleUser
from departments.models import DepartmentCourse, DepartmentStatistic
from teachers.models import Teacher
from hod.models import Head
from courses.models import Course
from academics.models import Level
from django.contrib import messages

def dashboard(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")

    # Head → Department eşleşmesi
    hod = Head.objects.filter(head_user__username=username, is_active=True).first()
    if not hod:
        return render(request, "hod/no_department.html")

    department = hod.department

    # Ders ekleme işlemi
    if request.method == "POST":
        course_id = request.POST.get("course")
        semester = request.POST.get("semester") or 1
        is_mandatory = request.POST.get("is_mandatory") == "on"

        if course_id:
            DepartmentCourse.objects.create(
                department=department,
                course_id=course_id,
                semester=semester,
                is_mandatory=is_mandatory,
            )
        return redirect("hod:dashboard")

    stats, _ = DepartmentStatistic.objects.get_or_create(department=department)
    courses = Course.objects.all()
    dept_courses = DepartmentCourse.objects.filter(department=department).select_related("course")
    teachers = Teacher.objects.filter(department=department)
    pending_courses = Course.objects.filter(created_by_head=hod, status="PENDING")

    return render(request, "hod/dashboard.html", {
        "username": username,
        "department": department,
        "stats": stats,
        "courses": courses,
        "dept_courses": dept_courses,
        "teachers": teachers,
        "pending_courses": pending_courses,
    })


def delete_course(request, pk):
    username = request.session.get("username")
    hod = Head.objects.filter(head_user__username=username).first()
    if not hod:
        return redirect("hod:dashboard")

    course = get_object_or_404(DepartmentCourse, pk=pk)

    if course.department != hod.department:
        return redirect("hod:dashboard")

    course.delete()
    return redirect("hod:dashboard")


def teacher_detail(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)

    return render(request, "hod/teacher_detail.html", {
        "teacher": teacher
    })

def create_course(request):
    username = request.session.get("username")
    hod = Head.objects.filter(head_user__username=username).first()

    levels = Level.objects.all()

    if request.method == "POST":
        code = request.POST["code"].strip().upper()

        # Duplicate course kontrolü
        if Course.objects.filter(code=code).exists():
            messages.error(request, "Bu ders kodu zaten mevcut.")
            return redirect("hod:create_course")

        Course.objects.create(
            code=code,
            name=request.POST["name"],
            credit=request.POST["credit"],
            ects=request.POST["ects"],
            level_id=request.POST["level"],
            course_type=request.POST["course_type"],
            status="PENDING",
            created_by_head=hod,
        )

        messages.success(request, "Ders oluşturuldu, Dean onayına gönderildi.")

        # ⭐⭐ İşte tam burası! ⭐⭐
        return redirect("hod:dashboard")  # → Ana sayfaya döner

    return render(request, "hod/create_course.html", {
        "levels": levels
    })

