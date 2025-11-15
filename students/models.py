from departments.models import Department
from academics.models import Level
from django.db import models
from teachers.models import Teacher
from accounts.models import SimpleUser

class Student(models.Model):
    user = models.OneToOneField(SimpleUser, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=100)
    student_no = models.CharField(max_length=10, unique=True)
    email = models.EmailField(unique=True)  # ⭐ YENİ EKLENDİ
    departments = models.ManyToManyField(Department, related_name="students", blank=True)
    advisor = models.ForeignKey("teachers.Teacher", on_delete=models.SET_NULL, null=True, blank=True)
    student_level = models.ForeignKey(Level, on_delete=models.SET_NULL, null=True, blank=True, related_name="student_levels")

    def __str__(self):
        return f"{self.student_no} - {self.full_name}"

