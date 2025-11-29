from django.shortcuts import render, redirect, get_object_or_404
from accounts.models import SimpleUser
from departments.models import DepartmentCourse, DepartmentStatistic
from teachers.models import Teacher, TeacherSchedule
from hod.models import Head
from courses.models import Course, CourseOffering, CourseAssessmentComponent
from academics.models import Level
from django.contrib import messages
from .models import TeacherCourseAssignment, TeacherPerformance
from django.utils import timezone


# ============================================================
# DASHBOARD
# ============================================================
def dashboard(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
    ).select_related("department").first()

    if not hod:
        return render(request, "hod/no_department.html")

    department = hod.department
    stats, _ = DepartmentStatistic.objects.get_or_create(department=department)

    dept_courses = DepartmentCourse.objects.filter(
        department=department
    ).select_related("course")

    teachers = Teacher.objects.filter(department=department)

    # ✅ Dean onayı kalktığı için pending_course kavramı artık yok
    return render(request, "hod/dashboard.html", {
        "username": username,
        "department": department,
        "stats": stats,
        "dept_courses": dept_courses,
        "teachers": teachers,
    })


# ============================================================
# DERS OLUŞTURMA
# ============================================================
def create_course(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
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
        semester = request.POST.get("semester") or 1


        if Course.objects.filter(code=code).exists():
            error = "Bu kodla kayıtlı bir ders zaten var."

        if not error:
            # -----------------------------
            # DERS OLUŞTUR
            # -----------------------------
            course = Course.objects.create(
                code=code,
                name=name,
                credit=credit,
                ects=ects,
                level_id=level_id,
                course_type=course_type,
                created_by_head=hod,
                semester=semester,
                is_active=True,  # ✅ Direkt aktif
            )

            # -----------------------------
            # DERSİ BÖLÜME EKLE
            # -----------------------------
            DepartmentCourse.objects.create(
                department=department,
                course=course,
                semester=semester,
                is_mandatory=True,
            )

            # Önkoşullar
            prereq_ids = request.POST.getlist("prerequisites")
            course.prerequisites.set(prereq_ids)

            # -----------------------------
            # ÖĞRETMEN ATAMASI
            # -----------------------------
            teacher_ids = request.POST.getlist("teachers")
            for t_id in teacher_ids:
                teacher = Teacher.objects.get(id=t_id)
                course.teachers.add(teacher)

                TeacherCourseAssignment.objects.get_or_create(
                    teacher=teacher,
                    course=course,
                    defaults={
                        "semester": semester,
                        "year": timezone.now().year,
                        "is_active": True,
                    }
                )

            messages.success(request, "Ders başarıyla oluşturuldu ve aktif hale getirildi.")
            return redirect("hod:dashboard")

    return render(request, "hod/create_course.html", {
        "department": department,
        "teachers": teachers,
        "level_list": level_list,
        "all_courses": all_courses,
        "error": error,
    })



# ============================================================
# VAR OLAN DERSİ BÖLÜME EKLEME
# ============================================================
def add_existing_course(request):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(head_user__username=username, is_active=True).first()

    if not hod:
        return redirect("hod:dashboard")

    department = hod.department
    all_courses = Course.objects.filter(is_active=True)

    error = None

    if request.method == "POST":
        course_id = request.POST.get("course_id")
        course = get_object_or_404(Course, id=course_id)

        # Zaten o bölümde varsa tekrar eklenmesin
        if DepartmentCourse.objects.filter(department=department, course=course).exists():
            error = "Bu ders zaten bölümde mevcut."
        else:
            DepartmentCourse.objects.create(
                department=department,
                course=course,
                semester=course.semester,
                is_mandatory=False,
            )
            messages.success(request, "Ders başarıyla bölüme eklendi.")
            return redirect("hod:dashboard")

    return render(request, "hod/add_existing_course.html", {
        "department": department,
        "all_courses": all_courses,
        "error": error,
    })

# ============================================================
# DERS DETAY SAYFASI (Head tarafından görüntülenir)
# ============================================================
def course_detail(request, course_id):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
    ).select_related("department").first()

    if not hod:
        return redirect("hod:dashboard")

    # 1) DepartmentCourse kaydını bul
    dept_course = get_object_or_404(
        DepartmentCourse.objects.select_related("course", "department"),
        pk=course_id
    )
    course = dept_course.course

    # 2) Bu derse bağlı şubeleri getir
    offerings = CourseOffering.objects.filter(course=course)

    # 3) Önkoşul dersleri ve mevcut öğretmen atamalarını al
    all_courses = Course.objects.exclude(id=course.id)
    current_prereq_ids = list(course.prerequisites.values_list("id", flat=True))

    assigned_teachers = (
        TeacherCourseAssignment.objects
        .filter(course=course, is_active=True)
        .select_related("teacher", "teacher__user")
        .order_by("semester", "teacher__academic_title")
    )

    return render(request, "hod/course_detail.html", {
        "dept_course": dept_course,
        "course": course,
        "offerings": offerings,
        "all_courses": all_courses,
        "current_prereq_ids": current_prereq_ids,
        "assigned_teachers": assigned_teachers,
    })

# ============================================================
# DERS DÜZENLEME SAYFASI (Head tarafından)
# ============================================================
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
    level_list = Level.objects.all()
    all_courses = Course.objects.exclude(id=course.id)
    current_prereq_ids = list(course.prerequisites.values_list("id", flat=True))

    selected_teacher_ids = list(
        course.teachers.values_list("id", flat=True)
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

        prereq_ids = request.POST.getlist("prerequisites")
        course.prerequisites.set(prereq_ids)

        course.save()

        dept_course.semester = request.POST.get("semester") or 1
        dept_course.save()

        # -----------------------------
        # ÖĞRETMEN GÜNCELLEME
        # -----------------------------
        new_ids = set(map(int, request.POST.getlist("teachers")))

        # 1) TeacherCourseAssignment tablosu güncelle
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

        # 2) M2M güncelle
        course.teachers.set(new_ids)

        messages.success(request, "Ders başarıyla güncellendi.")
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

# ============================================================
# DERS SİLME (Head tarafından)
# ============================================================
def delete_course(request, pk):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
    ).select_related("department").first()

    if not hod:
        return redirect("hod:dashboard")

    dept_course = get_object_or_404(DepartmentCourse, pk=pk)

    # 🔒 Sadece kendi bölümündeki dersi silebilir
    if dept_course.department != hod.department:
        messages.warning(request, "Bu ders sizin bölümünüze ait değil.")
        return redirect("hod:dashboard")

    course = dept_course.course  # Silinecek asıl ders nesnesi

    # -----------------------------
    # 1️⃣ İlgili öğretmen atamalarını kaldır
    # -----------------------------
    TeacherCourseAssignment.objects.filter(course=course).delete()

    # -----------------------------
    # 2️⃣ M2M (Course.teachers) bağlantısını temizle
    # -----------------------------
    course.teachers.clear()

    # -----------------------------
    # 3️⃣ DepartmentCourse kaydını sil
    # -----------------------------
    dept_course.delete()

    messages.success(request, "Ders ve ilgili öğretmen atamaları başarıyla silindi.")
    return redirect("hod:dashboard")

# ============================================================
# DERS ŞUBE (OFFERING) EKLEME SAYFASI
# ============================================================
def add_offering(request, course_id):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
    ).select_related("department").first()

    if not hod:
        return redirect("hod:dashboard")

    course = get_object_or_404(Course, id=course_id)

    if request.method == "POST":
        year = request.POST.get("year")
        semester = request.POST.get("semester")
        section = request.POST.get("section")
        max_students = request.POST.get("max_students", 30)
        location = request.POST.get("location", "")

        CourseOffering.objects.create(
            course=course,
            year=year,
            semester=semester,
            section=section,
            max_students=max_students,
            location=location
        )

        messages.success(request, "Yeni ders şubesi başarıyla oluşturuldu.")
        return redirect("hod:course_detail", course_id=course.id)

    return render(request, "hod/add_offering.html", {
        "course": course,
    })

# ============================================================
# ÖĞRETMEN DETAY SAYFASI (Head tarafından görüntülenir)
# ============================================================
def teacher_detail(request, pk):
    if request.session.get("role") != "HOD":
        return redirect("login")

    username = request.session.get("username")
    hod = Head.objects.filter(
        head_user__username=username,
        is_active=True
    ).select_related("department").first()

    if not hod:
        return redirect("hod:dashboard")

    teacher = get_object_or_404(Teacher, pk=pk, department=hod.department)

    # 🔥 Artık aktif atamaları direkt çekiyoruz
    assigned_courses = (
        teacher.assignments
        .filter(is_active=True)
        .select_related("course")
        .order_by("course__name")
    )

    return render(request, "hod/teacher_detail.html", {
        "teacher": teacher,
        "assigned_courses": assigned_courses,
    })
