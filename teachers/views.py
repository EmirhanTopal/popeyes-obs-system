from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone
import departments.models
from accounts.models import SimpleUser
from django.db.models import Prefetch
from courses.models import (
    Course,
    CourseAssessmentComponent,
    ComponentLearningProgramRelation,
    ComponentLearningRelation,
    LearningProgramRelation,
    CourseEnrollment,
    CourseGrade
)
from outcomes.models import ProgramOutcome, LearningOutcome
from .models import Teacher, TeacherSchedule, OfficeHour
from .forms import (
    TeacherProfileForm,
    TeacherScheduleForm,
    OfficeHourForm,
    TeacherContactInfoForm
)
from django.db.models import Prefetch
from outcomes.services import (
    compute_student_learning_outcomes,
    compute_student_program_outcomes, compute_and_save_student_program_outcomes
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
    active_courses = teacher.courses.all()


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

    username = request.session.get("username")

    teacher = Teacher.objects.filter(user__username=username).first()

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

    return render(request, "teachers/manage_schedule.html", {
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

    # 1) SimpleUser objesini bul
    simple_user = SimpleUser.objects.filter(username=username).first()

    if not simple_user:
        messages.error(request, "Kullanıcı bulunamadı.")
        return redirect("login")

    # 2) Teacher objesini bul
    teacher = Teacher.objects.filter(user=simple_user).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    # 3) Öğretmenin dersleri (ManyToMany)
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


def manage_components(request, course_id):
    if not request.session.get("username"):
        messages.error(request, "Bu sayfayı görüntülemek için giriş yapmalısınız.")
        return redirect("login")

    if request.session.get("role") != "TEACHER":
        messages.error(request, "Bu sayfa yalnızca öğretmenler içindir.")
        return redirect("teachers:dashboard")

    username = request.session.get("username")
    user = SimpleUser.objects.filter(username=username).first()
    teacher = Teacher.objects.filter(user=user).first()
    course = get_object_or_404(Course, id=course_id, teachers=teacher)

    from django.db.models import Prefetch

    components = CourseAssessmentComponent.objects.filter(course=course).prefetch_related(
        Prefetch("learning_relations", queryset=ComponentLearningRelation.objects.select_related("learning_outcome"))
    ).order_by("type")

    learning_outcomes = LearningOutcome.objects.filter(course=course)
    program_outcomes = ProgramOutcome.objects.all()

    if request.method == "POST":
        types = request.POST.getlist("type[]")
        weights = request.POST.getlist("weight[]")

        existing_components = set(components.values_list("id", flat=True))
        used_components = set()
        total_component_weight = 0

        # ===========================================
        # 1️⃣ Component ve %LO kayıtları
        # ===========================================
        count = max(len(types), len(weights))
        for i in range(count):
            t = types[i] if i < len(types) else ""
            w = weights[i] if i < len(weights) else ""

            if not t or not w:
                continue

            total_component_weight += int(w)
            comp_id = request.POST.get(f"component_id_{i}")

            if comp_id:
                comp, _ = CourseAssessmentComponent.objects.update_or_create(
                    id=comp_id,
                    defaults={"course": course, "type": t, "weight": w},
                )
            else:
                comp = CourseAssessmentComponent.objects.create(
                    course=course, type=t, weight=w
                )
            used_components.add(comp.id)

            # Mevcut LO ilişkilerini sil ve yeniden ekle
            ComponentLearningRelation.objects.filter(component=comp).delete()
            lo_ids = request.POST.getlist(f"relation_lo_{i}[]")
            lo_ws = request.POST.getlist(f"relation_lw_{i}[]")

            for lo_id, lw in zip(lo_ids, lo_ws):
                if lo_id:
                    ComponentLearningRelation.objects.create(
                        component=comp,
                        learning_outcome_id=int(lo_id),
                        weight=float(lw or 0.0),
                    )

        # Artık kullanılmayan component’leri temizle
        CourseAssessmentComponent.objects.filter(course=course).exclude(id__in=used_components).delete()

        # ===========================================
        # 2️⃣ Program Output (LO → PO)
        # ===========================================
        map_los = request.POST.getlist("po_map_lo[]")
        map_ws = request.POST.getlist("po_map_w[]")
        map_pos = request.POST.getlist("po_map_po[]")

        # Önce mevcutları temizle
        LearningProgramRelation.objects.filter(learning_outcome__course=course).delete()

        seen = set()
        for lo_id, w, po_id in zip(map_los, map_ws, map_pos):
            if not lo_id or not po_id:
                continue
            key = (lo_id, po_id)
            if key in seen:
                continue
            seen.add(key)

            LearningProgramRelation.objects.get_or_create(
                learning_outcome_id=int(lo_id),
                program_outcome_id=int(po_id),
                defaults={"weight": float(w or 0.0)}
            )

        # ===========================================
        # Uyarı / başarı mesajı
        # ===========================================
        if total_component_weight != 100:
            messages.warning(request, f"Bileşen ağırlıkları %{total_component_weight}. Toplam %100 olmalı.")
        else:
            messages.success(request, "Bileşenler ve Program Output eşlemeleri kaydedildi. ✅")

        return redirect("teachers:manage_components", course_id=course.id)

    lo_po_maps = LearningProgramRelation.objects.filter(
        learning_outcome__course=course
    ).select_related("learning_outcome", "program_outcome")

    return render(request, "teachers/manage_components.html", {
        "course": course,
        "components": components,
        "learning_outcomes": learning_outcomes,
        "program_outcomes": program_outcomes,
        "lo_po_maps": lo_po_maps,
    })



def manage_learning_outcomes(request, course_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")

    username = request.session.get("username")
    user = SimpleUser.objects.filter(username=username).first()
    teacher = Teacher.objects.filter(user=user).first()
    course = get_object_or_404(Course, id=course_id, teachers=teacher)

    # Düzeltildi:
    outcomes = course.course_learning_outcomes.all()

    if request.method == "POST":
        code = request.POST.get("code")
        description = request.POST.get("description")
        if code and description:
            LearningOutcome.objects.create(course=course, code=code, description=description)
            messages.success(request, "Learning Outcome eklendi.")
            return redirect("teachers:manage_learning_outcomes", course_id=course.id)

    return render(request, "teachers/manage_learning_outcomes.html", {
        "course": course,
        "outcomes": outcomes,
    })

# ===============================================================
#  NOT GİRİŞİ (ÖĞRETMEN)
# ===============================================================
from django.db.models import Prefetch


def manage_grades(request, course_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")

    username = request.session.get("username")
    user = SimpleUser.objects.filter(username=username).first()
    teacher = Teacher.objects.filter(user=user).first()

    if not teacher:
        messages.error(request, "Öğretmen profili bulunamadı.")
        return redirect("login")

    course = get_object_or_404(
        Course,
        id=course_id,
        teachers=teacher,
        is_active=True
    )

    # Ders bileşenleri
    components = CourseAssessmentComponent.objects.filter(course=course).order_by("type")

    # Derse kayıtlı öğrenciler
    enrollments = CourseEnrollment.objects.filter(
        course=course,
        is_active=True,
        student__courses=course
    ).select_related("student")

    # POST: Not kaydet
    if request.method == "POST":
        for enrollment in enrollments:
            for comp in components:
                field_name = f"grade_{enrollment.id}_{comp.id}"
                score = request.POST.get(field_name)
                if score is not None and score.strip() != "":
                    score = float(score)
                    grade, created = CourseGrade.objects.get_or_create(
                        enrollment=enrollment,
                        component=comp
                    )
                    grade.score = score
                    grade.save()

        # 🔹 Notlar kaydedildikten sonra LO ve PO skorlarını yeniden hesapla
        for enrollment in enrollments:
            compute_and_save_student_program_outcomes(enrollment.student)

        messages.success(request, "Notlar kaydedildi ve Outcome skorları güncellendi ✅")

    # 🧩 Notları sözlüğe al
    grades = CourseGrade.objects.filter(enrollment__course=course)
    grade_map = {(int(g.enrollment_id), int(g.component_id)): float(g.score) for g in grades}

    return render(request, "teachers/manage_grades.html", {
        "course": course,
        "components": components,
        "enrollments": enrollments,
        "grades": grade_map,
    })