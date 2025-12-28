from django.db import models
from accounts.models import SimpleUser

class Dean(models.Model):
    teacher = models.OneToOneField(
        "teachers.Teacher",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="dean_role"
    )
    faculty = models.ForeignKey(
        'faculty.Faculty',
        on_delete=models.CASCADE,
        related_name='dean'
    )

    def __str__(self):
        if self.teacher:
            return f"{self.teacher.full_name} ({self.faculty.full_name})"
        return f"(Teacher atanmadı) - {self.faculty.full_name}"


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
