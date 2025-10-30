# dean/views.py
from django.shortcuts import render, redirect
from django.contrib import messages
from accounts.decorators import require_role

from academics.models import Department, Course
from students.models import Student
from teachers.models import Teacher
from .forms import DepartmentForm, CourseForm, TeacherForm, StudentForm


@require_role("DEAN")
def dashboard(request):
    dept_form = DepartmentForm(prefix="dept")
    course_form = CourseForm(prefix="course")
    teacher_form = TeacherForm(prefix="teacher")
    student_form = StudentForm(prefix="student")

    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create_department":
            dept_form = DepartmentForm(request.POST, prefix="dept")
            if dept_form.is_valid():
                dept_form.save()
                messages.success(request, "Bölüm eklendi.")
                return redirect("dean_dashboard")

        elif action == "create_course":
            course_form = CourseForm(request.POST, prefix="course")
            if course_form.is_valid():
                course_form.save()
                messages.success(request, "Ders eklendi.")
                return redirect("dean_dashboard")

        elif action == "create_teacher":
            teacher_form = TeacherForm(request.POST, prefix="teacher")
            if teacher_form.is_valid():
                teacher_form.save()
                messages.success(request, "Öğretmen eklendi.")
                return redirect("dean_dashboard")

        elif action == "create_student":
            student_form = StudentForm(request.POST, prefix="student")
            if student_form.is_valid():
                # M2M varsa önce instance, sonra save_m2m
                student = student_form.save(commit=False)
                student.save()
                student_form.save_m2m()
                messages.success(request, "Öğrenci eklendi.")
                return redirect("dean_dashboard")

        else:
            messages.error(request, "Geçersiz işlem.")

    context = {
        "dept_form": dept_form,
        "course_form": course_form,
        "teacher_form": teacher_form,
        "student_form": student_form,
        # listeler (sayfa altı özet)
        "departments": Department.objects.all().order_by("code"),
        "courses": Course.objects.prefetch_related("department").all().order_by("code"),
        "teachers": Teacher.objects.all().order_by("name"),
        "students": (
            Student.objects.select_related("advisor")
            .prefetch_related("departments")
            .all()
            .order_by("student_no")
        ),
    }
    return render(request, "dean/dashboard.html", context)
