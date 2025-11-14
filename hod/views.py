from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import SimpleUser
from departments.models import DepartmentCourse, DepartmentStatistic
from teachers.models import Teacher,TeacherSchedule
from hod.models import Head
from courses.models import Course, CourseOffering
from academics.models import Level
from django.contrib import messages
from .models import TeacherCourseAssignment, TeacherPerformance
from django.utils import timezone

def dashboard(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(head_user__username=username, is_active=True).select_related("department").first()
    if not hod:
        return render(request, "hod/no_department.html")

    department = hod.department

    # istatistik
    stats, _ = DepartmentStatistic.objects.get_or_create(department=department)
    courses = Course.objects.all()
    dept_courses = DepartmentCourse.objects.filter(department=department).select_related("course")
    teachers = Teacher.objects.filter(department=department)
    pending_courses = Course.objects.filter(created_by_head=hod, status="PENDING")
    pending_department_courses = DepartmentCourse.objects.filter(
        department=department,
        approval_status="PENDING"
    )

    return render(request, "hod/dashboard.html", {
        "username": username,
        "department": department,
        "stats": stats,
        "courses": courses,
        "dept_courses": dept_courses,
        "teachers": teachers,
        "pending_department_courses": pending_department_courses,

    })

def add_offering(request, course_id):
    course = get_object_or_404(Course, id=course_id)

    # Henüz tasarlanmamışsa boş bir sayfa bile yeter
    return render(request, "hod/add_offering.html", {"course": course})


def create_course(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username, is_active=True
    ).select_related("department").first()

    if not hod:
        return redirect("hod:dashboard")

    department = hod.department
    teachers = Teacher.objects.filter(department=department)
    level_list = Level.objects.all()
    all_courses = Course.objects.all()

    error = None

    if request.method == "POST":
        code = request.POST.get("code", "").strip().upper()
        name = request.POST.get("name", "").strip()
        credit = request.POST.get("credit") or None
        ects = request.POST.get("ects") or None
        level_id = request.POST.get("level")
        course_type = request.POST.get("course_type")
        semester = request.POST.get("semester")
        midterm = int(request.POST.get("midterm_weight"))
        final = int(request.POST.get("final_weight"))
        assignment = int(request.POST.get("assignment_weight"))
        attendance = int(request.POST.get("attendance_weight"))

        total = midterm + final + assignment + attendance
        if total != 100:
            error = "Vize + Final + Ödev + Devam toplamı 100 olmalıdır."

        if Course.objects.filter(code=code).exists():
            error = "Bu kodla kayıtlı bir ders zaten var."

        if not error:
            course = Course.objects.create(
                code=code,
                name=name,
                credit=credit,
                ects=ects,
                level_id=level_id,
                course_type=course_type,
                status="PENDING",
                created_by_head=hod,
                semester=semester,
                midterm_weight=midterm,
                final_weight=final,
                assignment_weight=assignment,
                attendance_weight=attendance,
            )

            # Önkoşulları ekle
            prereq_ids = request.POST.getlist("prerequisites")
            course.prerequisites.set(prereq_ids)

            # Öğretmen atamaları
            teacher_ids = request.POST.getlist("teachers")
            for t_id in teacher_ids:
                TeacherCourseAssignment.objects.create(
                    teacher_id=t_id,
                    course=course,
                    semester=1,
                    year=timezone.now().year,
                    is_active=True
                )

            return redirect("hod:dashboard")

    return render(request, "hod/create_course.html", {
        "department": department,
        "teachers": teachers,
        "level_list": level_list,
        "all_courses": all_courses,
        "error": error,
    })



def course_detail(request, course_id):
    # 1) DepartmentCourse kaydını ve Course'u çek
    dept_course = get_object_or_404(
        DepartmentCourse.objects.select_related("course", "department"),
        pk=course_id
    )
    course = dept_course.course

    # 2) Açılmış şubeler
    offerings = CourseOffering.objects.filter(course=course)

    # 3) Önkoşul dersler (sadece listelemek için)
    all_courses = Course.objects.exclude(id=course.id)
    current_prereq_ids = list(course.prerequisites.values_list("id", flat=True))

    # 4) Bu derse atanmış öğretim görevlileri
    assigned_teachers = (
        TeacherCourseAssignment.objects
        .filter(course=course, is_active=True)
        .select_related("teacher", "teacher__user")
        .order_by("semester", "teacher__academic_title")
    )

    # ❗ Bu sayfa sadece GÖRÜNTÜLEME, burada POST ile kayıt yok
    context = {
        "dept_course": dept_course,
        "course": course,
        "offerings": offerings,
        "all_courses": all_courses,
        "current_prereq_ids": current_prereq_ids,
        "assigned_teachers": assigned_teachers,
    }
    return render(request, "hod/course_detail.html", context)




def course_edit(request, pk):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
    ).select_related("department").first()
    if not hod:
        return redirect("hod:dashboard")

    dept_course = get_object_or_404(
        DepartmentCourse.objects.select_related("course", "department"),
        pk=pk,
        department=hod.department,
    )
    course = dept_course.course
    teachers = Teacher.objects.filter(department=hod.department)

    # Yeni: level list ve pre-req listeleri
    level_list = Level.objects.all()
    all_courses = Course.objects.exclude(id=course.id)
    current_prereq_ids = list(course.prerequisites.values_list("id", flat=True))

    # mevcut atamalar
    selected_teacher_ids = list(
        TeacherCourseAssignment.objects.filter(course=course, is_active=True)
        .values_list("teacher_id", flat=True)
    )

    error = None

    if request.method == "POST":
        course.name = request.POST.get("name", "").strip()
        course.credit = request.POST.get("credit") or None
        course.ects = request.POST.get("ects") or None
        course.course_type = request.POST.get("course_type")
        level_id = request.POST.get("level")

        if level_id:
            course.level_id = level_id

        # Önkoşullar
        prereq_ids = request.POST.getlist("prerequisites")
        course.prerequisites.set(prereq_ids)

        course.save()

        # bölüm dersi ayarları
        dept_course.semester = request.POST.get("semester") or 1
        dept_course.is_mandatory = bool(request.POST.get("is_mandatory"))
        dept_course.save()

        # öğretmen atamasını güncelle
        new_ids = set(map(int, request.POST.getlist("teachers")))
        TeacherCourseAssignment.objects.filter(course=course).exclude(
            teacher_id__in=new_ids
        ).delete()

        for t_id in new_ids:
            TeacherCourseAssignment.objects.get_or_create(
                teacher_id=t_id,
                course=course,
                defaults={
                    "semester": dept_course.semester,
                    "year": timezone.now().year,
                    "is_active": True,
                }
            )

        return redirect("hod:course_detail", course_id=dept_course.id)

    return render(request, "hod/course_edit.html", {
        "department": hod.department,
        "dept_course": dept_course,
        "course": course,
        "teachers": teachers,
        "selected_teacher_ids": selected_teacher_ids,
        "level_list": level_list,
        "all_courses": all_courses,
        "current_prereq_ids": current_prereq_ids,
        "error": error,
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

def add_existing_course(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(head_user__username=username, is_active=True).first()

    if not hod:
        return redirect("hod:dashboard")

    department = hod.department
    all_courses = Course.objects.filter(status="APPROVED")

    error = None

    if request.method == "POST":
        course_id = request.POST.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        # Zaten o bölümde varsa tekrar eklenmesin
        if DepartmentCourse.objects.filter(department=department, course=course).exists():
            error = "Bu ders zaten bölümde mevcut."
        else:
            # DEAN ONAYI İÇİN PENDING OLARAK İŞARETLİYORUZ
            DepartmentCourse.objects.create(
                department=department,
                course=course,
                semester=course.semester,
                is_mandatory=False,
                approval_status="PENDING"
            )
            messages.success(request, "Ders bölüme eklemek için onaya gönderildi.")
            return redirect("hod:dashboard")

    return render(request, "hod/add_existing_course.html", {
        "department": department,
        "all_courses": all_courses,
        "error": error,
    })
