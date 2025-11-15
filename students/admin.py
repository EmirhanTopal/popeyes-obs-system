# students/admin.py
from django.contrib import admin
from .models import Student, StudentCourseEnrollment, CourseAttendance

@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_id', 'full_name', 'department', 'level', 'status', 'registration_year']
    list_filter = ['department', 'level', 'status', 'registration_year']
    search_fields = ['student_id', 'user__first_name', 'user__last_name']
    list_editable = ['status']

@admin.register(StudentCourseEnrollment)
class StudentCourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'enrollment_type', 'is_active', 'enrolled_at']
    list_filter = ['enrollment_type', 'is_active', 'course']

@admin.register(CourseAttendance)
class CourseAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date', 'hours_missed']
    list_filter = ['course', 'date']