from django.db import models
from departments.models import Department
from academics.models import Level  # eğer Level ayrı bir app’teyse, buna göre ayarla

class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ("POOL", "Havuz Dersi"),
        ("FACULTY", "Fakülte Dersi"),
        ("DEPARTMENT", "Bölüm Dersi"),
    ]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    department = models.ManyToManyField(Department, related_name="courses")
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="courses")
    credit = models.FloatField(null=True, blank=True)
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        verbose_name="Ders Türü"
    )

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_course_type_display()})"
