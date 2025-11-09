from django.contrib import admin

# Register your models here.
# dean/admin.py
from django.contrib import admin
from .models import Dean, DepartmentHeadApproval, CourseApproval, FacultySettings, FacultyReport

@admin.register(Dean)
class DeanAdmin(admin.ModelAdmin):
    list_display = ('user', 'faculty')
    search_fields = ('user__username', 'faculty__name')

@admin.register(DepartmentHeadApproval)
class DepartmentHeadApprovalAdmin(admin.ModelAdmin):
    list_display = ('department', 'new_head', 'status', 'approved_by', 'created_at')
    list_filter = ('status',)
    actions = ['approve_head', 'reject_head']

    def approve_head(self, request, queryset):
        queryset.update(status='APPROVED')
    approve_head.short_description = "Seçili başkan atamalarını onayla"

    def reject_head(self, request, queryset):
        queryset.update(status='REJECTED')
    reject_head.short_description = "Seçili başkan atamalarını reddet"

@admin.register(CourseApproval)
class CourseApprovalAdmin(admin.ModelAdmin):
    list_display = ('course', 'requested_by', 'status', 'approved_by', 'created_at')
    list_filter = ('status',)
    search_fields = ('course__name', 'requested_by__user__username')

@admin.register(FacultySettings)
class FacultySettingsAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'max_students_per_class', 'max_courses_per_student', 'grading_system', 'updated_at')

@admin.register(FacultyReport)
class FacultyReportAdmin(admin.ModelAdmin):
    list_display = ('faculty', 'semester', 'average_gpa', 'total_students', 'total_teachers')
    list_filter = ('semester',)
