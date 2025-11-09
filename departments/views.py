from django.db import models
from faculty.models import Faculty
from courses.models import Course
from teachers.models import Teacher

class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments")
    head = models.OneToOneField(
        Teacher, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="managed_department", verbose_name="Bölüm Başkanı"
    )
    quota = models.PositiveIntegerField(default=100, verbose_name="Kontenjan")

    def __str__(self):
        return f"{self.code} - {self.name}"


class DepartmentCourse(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="department_courses")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="course_departments")
    semester = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.department.name} - {self.course.name}"


class DepartmentStatistic(models.Model):
    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name="statistics")
    student_count = models.PositiveIntegerField(default=0)
    teacher_count = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # yüzde

    def __str__(self):
        return f"{self.department.name} - % {self.success_rate}"


class DepartmentReport(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="reports")
    title = models.CharField(max_length=100)
    content = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.department.name}"
