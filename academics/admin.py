# academics/admin.py
from django.contrib import admin
from departments.models import Department
from academics.models import Level
from django.db import models
from teachers.models import Teacher
from faculty.models import Faculty
from courses.models import Course





@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ("number", "name")






