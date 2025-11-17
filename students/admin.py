# students/admin.py
from django.contrib import admin
from .models import Student, StudentCourseEnrollment, CourseAttendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_no', 'full_name', 'email', 'advisor_display', 'level_display']
    search_fields = ['student_no', 'full_name', 'email']
    list_filter = ['student_level']

    def advisor_display(self, obj):
        return obj.advisor.full_name if obj.advisor else "-"

    advisor_display.short_description = "Danışman"

    def level_display(self, obj):
        return obj.student_level.name if obj.student_level else "-"

    level_display.short_description = "Seviye"

@admin.register(StudentCourseEnrollment)
class StudentCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_type', 'is_active', 'enrolled_at']
    list_filter = ['enrollment_type', 'is_active', 'course']

@admin.register(CourseAttendance)
class CourseAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date', 'hours_missed']
    list_filter = ['course', 'date']