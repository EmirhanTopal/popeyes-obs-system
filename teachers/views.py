from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from .models import Teacher, TeacherSchedule, OfficeHour
from .forms import (
    TeacherProfileForm,
    TeacherScheduleForm,
    OfficeHourForm,
    TeacherContactInfoForm
)


# ===============================================================
#  ÖĞRETMEN DASHBOARD
# ===============================================================
def teacher_dashboard(request):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    username = request.session.get("username")

    teacher = Teacher.objects.filter(user__username=username).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    # 🔥 ÖNEMLİ: Öğretmene atanan dersler (ManyToMany)
    active_courses = teacher.courses.filter(is_active=True)

    # Yaklaşan programlar
    upcoming_schedules = teacher.schedules.all().order_by("day_of_week", "start_time")[:5]

    # Aktif ofis saatleri
    active_office_hours = teacher.office_hours.filter(is_active=True)

    context = {
        "teacher": teacher,
        "active_courses": active_courses,
        "total_students": 0,  # İstersen burada kayıtlı öğrencileri saydırırım
        "upcoming_schedules": upcoming_schedules,
        "active_office_hours": active_office_hours,
    }

    return render(request, "teachers/dashboard.html", context)



# ===============================================================
#  PROFİL
# ===============================================================
def teacher_profile(request):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    if request.method == "POST":
        form = TeacherProfileForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil başarıyla güncellendi.")
            return redirect("teachers:profile")
    else:
        form = TeacherProfileForm(instance=teacher)

    return render(request, "teachers/profile.html", {
        "teacher": teacher,
        "form": form,
    })



# ===============================================================
#  İLETİŞİM BİLGİSİ GÜNCELLEME
# ===============================================================
def update_contact_info(request):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    if request.method == "POST":
        form = TeacherContactInfoForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "İletişim bilgileri güncellendi.")
            return redirect("teachers:profile")
    else:
        form = TeacherContactInfoForm(instance=teacher)

    return render(request, "teachers/update_contact_info.html", {
        "teacher": teacher,
        "form": form,
    })



# ===============================================================
#  PROGRAM (SCHEDULE)
# ===============================================================
def manage_schedule(request):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    schedules = teacher.schedules.all()

    if request.method == "POST":
        form = TeacherScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.teacher = teacher
            schedule.save()
            messages.success(request, "Program başarıyla eklendi.")
            return redirect("teachers:manage_schedule")
    else:
        form = TeacherScheduleForm()

    return render(request, "teachers/schedule.html", {
        "teacher": teacher,
        "schedules": schedules,
        "form": form,
    })



# ===============================================================
#  OFİS SAATLERİ
# ===============================================================
def manage_office_hours(request):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    office_hours = teacher.office_hours.all()

    if request.method == "POST":
        form = OfficeHourForm(request.POST)
        if form.is_valid():
            oh = form.save(commit=False)
            oh.teacher = teacher
            oh.save()
            messages.success(request, "Ofis saati eklendi.")
            return redirect("teachers:manage_office_hours")
    else:
        form = OfficeHourForm()

    return render(request, "teachers/office_hours.html", {
        "teacher": teacher,
        "office_hours": office_hours,
        "form": form,
    })



# ===============================================================
#  DERLERİM
# ===============================================================
def course_management(request):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    username = request.session.get("username")

    teacher = Teacher.objects.filter(user__username=username).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    # 🔥 Öğretmene atanmış dersler (ManyToMany)
    courses = teacher.courses.filter(is_active=True)

    return render(request, "teachers/course_management.html", {
        "teacher": teacher,
        "courses": courses,
    })



# ===============================================================
#  DERS ÇIKTILARI
# ===============================================================
def manage_learning_outcomes(request, course_id):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    course = get_object_or_404(
        Course,
        id=course_id,
        teachers=teacher,
        is_active=True
    )

    from .forms import LearningOutcomeForm
    learning_outcomes = course.learning_outcomes.all()

    if request.method == "POST":
        form = LearningOutcomeForm(request.POST)
        if form.is_valid():
            outcome = form.save(commit=False)
            outcome.course = course
            outcome.created_by = teacher
            outcome.save()
            messages.success(request, "Öğrenme çıktısı eklendi.")
            return redirect("teachers:manage_learning_outcomes", course_id=course_id)
    else:
        form = LearningOutcomeForm()

    return render(request, "teachers/learning_outcomes.html", {
        "teacher": teacher,
        "course": course,
        "learning_outcomes": learning_outcomes,
        "form": form,
    })



# ===============================================================
#  NOT YÖNETİMİ
# ===============================================================
def grade_management(request, course_id):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    course = get_object_or_404(
        Course,
        id=course_id,
        teachers=teacher,
        is_active=True
    )

    enrollments = CourseEnrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related("student")

    return render(request, "teachers/grade_management.html", {
        "teacher": teacher,
        "course": course,
        "enrollments": enrollments,
    })



# ===============================================================
#  YOKLAMA
# ===============================================================
def attendance_management(request, course_id):

    if request.session.get("role") != "TEACHER":
        return redirect("login")

    teacher = Teacher.objects.filter(user=request.user).first()

    course = get_object_or_404(
        Course,
        id=course_id,
        teachers=teacher,
        is_active=True
    )

    enrollments = CourseEnrollment.objects.filter(
        course=course,
        is_active=True
    ).select_related("student")

    return render(request, "teachers/attendance_management.html", {
        "teacher": teacher,
        "course": course,
        "enrollments": enrollments,
    })
