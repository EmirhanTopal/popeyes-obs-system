# academics/admin.py
from django.contrib import admin
from .models import Faculty, Department, Level, Course


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'faculty_dean', 'dean')
    search_fields = ('full_name', 'faculty_dean')


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty')
    list_filter = ('faculty',)
    search_fields = ('code', 'name')


@admin.register(Level)
class LevelAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'course_type')
    list_filter = ('course_type', 'level')
    search_fields = ('code', 'name')
