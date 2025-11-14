from django.db import models
from accounts.models import SimpleUser
from django.db import models

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

class DepartmentHeadApproval(models.Model):
    department = models.ForeignKey('departments.Department', on_delete=models.CASCADE)
    new_head = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    approved_by = models.ForeignKey('Dean', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Beklemede'),
            ('APPROVED', 'Onaylandı'),
            ('REJECTED', 'Reddedildi'),
        ],
        default='PENDING'
    )
    created_at = models.DateTimeField(auto_now_add=True)


class CourseApproval(models.Model):
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE)
    requested_by = models.ForeignKey('teachers.Teacher', on_delete=models.CASCADE)
    approved_by = models.ForeignKey('Dean', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Beklemede'),
            ('APPROVED', 'Onaylandı'),
            ('REJECTED', 'Reddedildi'),
        ],
        default='PENDING'
    )
    reason = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


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
