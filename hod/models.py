from django.shortcuts import render, redirect
from accounts.models import SimpleUser
from departments.models import Department, DepartmentCourse, DepartmentStatistic
from courses.models import Course
from django.db import models
from django.contrib.auth import get_user_model
from teachers.models import Teacher

class Head(models.Model):
    head_user = models.OneToOneField(SimpleUser, on_delete=models.CASCADE, related_name="head_profile")
    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name="head")
    teacher_profile = models.OneToOneField(
        Teacher,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="head_role",
        help_text="Bu kullanıcı aynı zamanda öğretim görevlisiyse atanabilir."
    )

    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(null=True, blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bölüm Başkanı"
        verbose_name_plural = "Bölüm Başkanları"
        ordering = ["department"]

    def __str__(self):
        return f"{self.head_user.get_full_name()} — {self.department.name}"

    @property
    def full_name(self):
        return self.head_user.get_full_name()

    @property
    def email(self):
        return self.head_user.email

    @property
    def active_since(self):
        return f"{self.start_date} tarihinden beri aktif."


class TeacherCourseAssignment(models.Model):
    teacher = models.ForeignKey(
        Teacher,
        on_delete=models.CASCADE,
        related_name="assignments"  # 🔥 Bunu EKLE
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="assignments"
    )
    semester = models.PositiveIntegerField(default=1)
    year = models.PositiveIntegerField(default=2025)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Öğretmen-Ders Ataması"
        verbose_name_plural = "Öğretmen-Ders Atamaları"
        ordering = ["teacher", "course"]

    def __str__(self):
        return f"{self.teacher.full_name} — {self.course.name}"

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
    generated_by = models.ForeignKey(SimpleUser, on_delete=models.SET_NULL, null=True)
    report_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.report_type} ({self.created_at})"

