from django.db import models
from accounts.models import SimpleUser


class Dean(models.Model):
    user = models.OneToOneField(SimpleUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    faculty = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.CASCADE,
        related_name='dean_users'
    )

    def __str__(self):
        return f"{self.full_name} ({self.faculty.full_name})"


# ✅ Artık DepartmentHeadApproval ve CourseApproval kaldırıldı
# Çünkü Dean artık hiçbir onay mekanizmasında yer almayacak.


class FacultySettings(models.Model):
    faculty = models.OneToOneField('faculty.Faculty', on_delete=models.CASCADE)
    max_students_per_class = models.PositiveIntegerField(default=30)
    max_courses_per_student = models.PositiveIntegerField(default=8)
    grading_system = models.CharField(max_length=50, default="AA-FF")
    updated_at = models.DateTimeField(auto_now=True)


class FacultyReport(models.Model):
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.CASCADE)
    total_students = models.PositiveIntegerField()
    total_teachers = models.PositiveIntegerField()
    average_gpa = models.DecimalField(max_digits=3, decimal_places=2)
    semester = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)
