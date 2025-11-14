from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count
from django.utils import timezone
from .models import Teacher, TeacherSchedule, OfficeHour
from .forms import TeacherProfileForm, TeacherScheduleForm, OfficeHourForm,TeacherContactInfoForm
from courses.models import Course
from django.utils import timezone

def teacher_dashboard(request):

    # SIMPLEUSER kontrolü
    if request.session.get("role") != "TEACHER":
        return redirect("login")

    username = request.session.get("username")
    teacher = Teacher.objects.filter(user__username=username).first()

    if not teacher:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect("login")

    active_courses = teacher.courses.filter(is_active=True)
    upcoming_schedules = teacher.schedules.all().order_by('day_of_week', 'start_time')[:5]
    active_office_hours = teacher.office_hours.filter(is_active=True)

    context = {
        'teacher': teacher,
        'active_courses': active_courses,
        'total_students': 0,
        'upcoming_schedules': upcoming_schedules,
        'active_office_hours': active_office_hours,
    }

    return render(request, 'teachers/dashboard.html', context)

def teacher_profile(request):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        if request.method == 'POST':
            form = TeacherProfileForm(request.POST, instance=teacher)
            if form.is_valid():
                form.save()
                messages.success(request, 'Profil bilgileriniz başarıyla güncellendi.')
                return redirect('teachers:profile')
        else:
            form = TeacherProfileForm(instance=teacher)
        
        context = {
            'teacher': teacher,
            'form': form,
        }
        return render(request, 'teachers/profile.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def update_contact_info(request):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        
        if request.method == 'POST':
            form = TeacherContactInfoForm(request.POST, instance=teacher)
            if form.is_valid():
                form.save()
                messages.success(request, 'İletişim bilgileriniz başarıyla güncellendi.')
                return redirect('teachers:profile')
        else:
            form = TeacherContactInfoForm(instance=teacher)
        
        context = {
            'teacher': teacher,
            'form': form,
        }
        return render(request, 'teachers/update_contact_info.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def manage_schedule(request):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        schedules = teacher.schedules.all()
        
        if request.method == 'POST':
            form = TeacherScheduleForm(request.POST)
            if form.is_valid():
                schedule = form.save(commit=False)
                schedule.teacher = teacher
                schedule.save()
                messages.success(request, 'Program başarıyla eklendi.')
                return redirect('teachers:manage_schedule')
        else:
            form = TeacherScheduleForm()
        
        context = {
            'teacher': teacher,
            'schedules': schedules,
            'form': form,
        }
        return render(request, 'teachers/schedule.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def manage_office_hours(request):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        office_hours = teacher.office_hours.all()
        
        if request.method == 'POST':
            form = OfficeHourForm(request.POST)
            if form.is_valid():
                office_hour = form.save(commit=False)
                office_hour.teacher = teacher
                office_hour.save()
                messages.success(request, 'Ofis saati başarıyla eklendi.')
                return redirect('teachers:manage_office_hours')
        else:
            form = OfficeHourForm()
        
        context = {
            'teacher': teacher,
            'office_hours': office_hours,
            'form': form,
        }
        return render(request, 'teachers/office_hours.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def course_management(request):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        courses = teacher.courses.filter(is_active=True)
        
        context = {
            'teacher': teacher,
            'courses': courses,
        }
        return render(request, 'teachers/course_management.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def manage_learning_outcomes(request, course_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, teachers=teacher, is_active=True)
        
        if request.method == 'POST':
            form = LearningOutcomeForm(request.POST)
            if form.is_valid():
                learning_outcome = form.save(commit=False)
                learning_outcome.course = course
                learning_outcome.created_by = teacher
                learning_outcome.save()
                messages.success(request, 'Öğrenme çıktısı başarıyla eklendi.')
                return redirect('teachers:manage_learning_outcomes', course_id=course_id)
        else:
            form = LearningOutcomeForm()
        
        learning_outcomes = course.learning_outcomes.all()
        
        context = {
            'teacher': teacher,
            'course': course,
            'learning_outcomes': learning_outcomes,
            'form': form,
        }
        return render(request, 'teachers/learning_outcomes.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')


def edit_learning_outcome(request, outcome_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        learning_outcome = get_object_or_404(
            LearningOutcome, 
            id=outcome_id, 
            created_by=teacher
        )
        
        if request.method == 'POST':
            form = LearningOutcomeForm(request.POST, instance=learning_outcome)
            if form.is_valid():
                form.save()
                messages.success(request, 'Öğrenme çıktısı başarıyla güncellendi.')
                return redirect('teachers:manage_learning_outcomes', course_id=learning_outcome.course.id)
        else:
            form = LearningOutcomeForm(instance=learning_outcome)
        
        context = {
            'form': form,
            'learning_outcome': learning_outcome,
            'teacher': teacher,
        }
        return render(request, 'teachers/edit_learning_outcome.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def delete_learning_outcome(request, outcome_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        learning_outcome = get_object_or_404(
            LearningOutcome, 
            id=outcome_id, 
            created_by=teacher
        )
        
        course_id = learning_outcome.course.id
        learning_outcome.delete()
        messages.success(request, 'Öğrenme çıktısı başarıyla silindi.')
        return redirect('teachers:manage_learning_outcomes', course_id=course_id)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def grade_management(request, course_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, teachers=teacher, is_active=True)
        enrollments = CourseEnrollment.objects.filter(course=course, is_active=True).select_related('student')
        
        context = {
            'teacher': teacher,
            'course': course,
            'enrollments': enrollments,
        }
        return render(request, 'teachers/grade_management.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')

def attendance_management(request, course_id):
    if request.session.get("role") != "TEACHER":
        return redirect("login")
    try:
        teacher = Teacher.objects.get(user=request.user)
        course = get_object_or_404(Course, id=course_id, teachers=teacher, is_active=True)
        enrollments = CourseEnrollment.objects.filter(course=course, is_active=True).select_related('student')
        
        context = {
            'teacher': teacher,
            'course': course,
            'enrollments': enrollments,
        }
        return render(request, 'teachers/attendance_management.html', context)
    except Teacher.DoesNotExist:
        messages.error(request, "Öğretmen profiliniz bulunamadı.")
        return redirect('home')