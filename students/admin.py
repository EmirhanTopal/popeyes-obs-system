from django.contrib import admin
from .models import Student, StudentCourseEnrollment, CourseAttendance
from courses.models import CourseEnrollment


# ============================================================
# Student Admin
# ============================================================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_no', 'full_name', 'email', 'advisor_display', 'level_display']
    search_fields = ['student_no', 'full_name', 'email']
    list_filter = ['student_level']
    filter_horizontal = ['courses']

    def advisor_display(self, obj):
        return obj.advisor.full_name if obj.advisor else "-"
    advisor_display.short_description = "Danışman"

    def level_display(self, obj):
        return obj.student_level.name if obj.student_level else "-"
    level_display.short_description = "Seviye"

    def save_related(self, request, form, formsets, change):
        """
        M2M ilişkiler kaydedildikten sonra CourseEnrollment oluştur.
        """
        super().save_related(request, form, formsets, change)
        obj = form.instance  # kayıtlı öğrenci nesnesi

        from courses.models import CourseEnrollment
        for course in obj.courses.all():
            CourseEnrollment.objects.get_or_create(student=obj, course=course)

# ============================================================
# Attendance Admin (opsiyonel)
# ============================================================
@admin.register(CourseAttendance)
class CourseAttendanceAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'date', 'hours_missed']
    list_filter = ['course', 'date']
