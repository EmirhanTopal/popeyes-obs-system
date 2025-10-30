from django.db import models

from dean.models import Dean


class Faculty(models.Model):
    full_name = models.CharField(max_length=100)
    faculty_dean = models.CharField(max_length=100)
    dean = models.ForeignKey(Dean, on_delete=models.SET_NULL, null=True, blank=True, related_name="faculties")

class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE, related_name="departments")
    def __str__(self):
        return f"{self.code} - {self.name}"

class Level(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    #code: l1 , name : 1.sınıf gibi

    def __str__(self):
        return self.name

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
    credi = models.FloatField(null=True, blank=True)
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        verbose_name="Ders Türü"
    )

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_course_type_display()})"

