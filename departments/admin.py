from django.contrib import admin
from .models import Department, DepartmentCourse, DepartmentStatistic

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty',)
    search_fields = ('code', 'name',"faculty__full_name",)
    list_filter = ('faculty',)

@admin.register(DepartmentCourse)
class DepartmentCourseAdmin(admin.ModelAdmin):
    list_display = ('department', 'course', 'semester', 'is_mandatory')
    list_filter = ('department', 'semester', 'is_mandatory')
    autocomplete_fields = ('department', 'course')
    search_fields = (
        'department__name',
        'department__code',
        'course__name',
        'course__code',
    )


@admin.register(DepartmentStatistic)
class DepartmentStatisticAdmin(admin.ModelAdmin):
    list_display = ('department', 'student_count', 'teacher_count', 'success_rate')
    search_fields = ('department__name', 'department__code')
    list_filter = ('department__faculty',)
    autocomplete_fields = ('department',)

