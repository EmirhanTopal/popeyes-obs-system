from departments.models import Department
from academics.models import Level
from django.db import models
from teachers.models import Teacher

class Student(models.Model):
    full_name = models.CharField(max_length=100)
    student_no = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)  # ⭐ YENİ EKLENDİ
    departments = models.ManyToManyField(Department, related_name="students", blank=True)
    advisor = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name="advisees")
    student_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_levels")

    def __str__(self):
        return f"{self.student_no} - {self.full_name}"

