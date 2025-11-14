from django.db import models
from accounts.models import SimpleUser
from faculty.models import Faculty
class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments")
    quota = models.PositiveIntegerField(default=100)
    # Bölüm başkanı: doğrudan SimpleUser(HOD) bağlıyoruz
    head_user = models.OneToOneField(
        SimpleUser, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'HOD'}, related_name='headed_department'
    )

    def __str__(self):
        return f"{self.code} - {self.name}"

class DepartmentCourse(models.Model):
    APPROVAL_CHOICES = [
        ("PENDING", "Onay Bekliyor"),
        ("APPROVED", "Onaylandı"),
        ("REJECTED", "Reddedildi"),
    ]

    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="department_courses")
    course = models.ForeignKey('courses.Course', on_delete=models.CASCADE, related_name="course_departments")
    semester = models.PositiveIntegerField(default=1)
    is_mandatory = models.BooleanField(default=True)
    approval_status = models.CharField(max_length=20, choices=APPROVAL_CHOICES,default="PENDING")
    def __str__(self):
        return f"{self.department.name} - {self.course}"

class DepartmentStatistic(models.Model):
    department = models.OneToOneField(Department, on_delete=models.CASCADE, related_name="statistics")
    student_count = models.PositiveIntegerField(default=0)
    teacher_count = models.PositiveIntegerField(default=0)
    success_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)  # % değer

    def __str__(self):
        return f"{self.department.name} İstatistikleri"
