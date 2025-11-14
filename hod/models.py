from django.shortcuts import render, redirect
from accounts.models import SimpleUser
from departments.models import Department, DepartmentCourse, DepartmentStatistic
from courses.models import Course
from django.db import models
from django.contrib.auth import get_user_model
from teachers.models import Teacher

User = get_user_model()


# ----------------------------------------------------
# 📘 1) Ders Atama (Teacher ↔ Course)
# ----------------------------------------------------
class TeacherCourseAssignment(models.Model):
    """
    Head, öğretmenlere ders atar.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name="assignments")
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    semester = models.PositiveSmallIntegerField(default=1)
    year = models.PositiveIntegerField()  # Akademik yıl
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("teacher", "course", "semester", "year")

    def __str__(self):
        return f"{self.course.code} → {self.teacher.user.get_full_name()}"


# ----------------------------------------------------
# 📊 2) Bölüm Genel İstatistikleri
# ----------------------------------------------------
class DepartmentStatistic(models.Model):
    """
    Dashboard için bölüm istatistikleri.
    """
    department = models.OneToOneField(Department, on_delete=models.CASCADE)
    total_students = models.PositiveIntegerField(default=0)
    total_teachers = models.PositiveIntegerField(default=0)
    total_courses = models.PositiveIntegerField(default=0)
    success_rate = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.department.name} Statistics"


# ----------------------------------------------------
# 📚 3) Ders Bazlı İstatistikler
# ----------------------------------------------------
class CourseStatistic(models.Model):
    """
    Dersin kendi akademik istatistiği.
    """
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    avg_score = models.FloatField(default=0.0)
    pass_rate = models.FloatField(default=0.0)   # % kaçı geçti
    fail_rate = models.FloatField(default=0.0)   # % kaçı kaldı
    total_students = models.PositiveIntegerField(default=0)
    semester = models.PositiveSmallIntegerField(default=1)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("course", "department", "semester")

    def __str__(self):
        return f"{self.course.code} Stats"


# ----------------------------------------------------
# ⭐ 4) Öğretmen Performans Raporu
# ----------------------------------------------------
class TeacherPerformance(models.Model):
    """
    Öğretmenin performansına yönelik raporlar.
    """
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    avg_success_rate = models.FloatField(default=0.0)
    avg_attendance_rate = models.FloatField(default=0.0)
    student_feedback_score = models.FloatField(default=0.0)  # 1-5 arası değerlendirme
    semester = models.PositiveSmallIntegerField(default=1)
    year = models.PositiveIntegerField()
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("teacher", "course", "semester", "year")

    def __str__(self):
        return f"{self.teacher.user.get_full_name()} Performance"


# ----------------------------------------------------
# 📥 5) Head Tarafından Üretilen Rapor Logları
# ----------------------------------------------------
class HeadReportLog(models.Model):
    """
    Head tarafında oluşturulmuş raporların geçmişi.
    """
    department = models.ForeignKey(Department, on_delete=models.CASCADE)
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    report_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} ({self.created_at})"

