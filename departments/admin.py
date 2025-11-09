from django.contrib import admin
from .models import Department, DepartmentCourse, DepartmentStatistic

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty', 'quota', 'head_user')
    search_fields = ('code', 'name')
    list_filter = ('faculty',)

@admin.register(DepartmentCourse)
class DepartmentCourseAdmin(admin.ModelAdmin):
    list_display = ('department', 'course', 'semester', 'is_mandatory')
    list_filter = ('department', 'semester', 'is_mandatory')

@admin.register(DepartmentStatistic)
class DepartmentStatisticAdmin(admin.ModelAdmin):
    list_display = ('department', 'student_count', 'teacher_count', 'success_rate')
