"""from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import (
    TeacherCourseAssignment,
    DepartmentStatistic,
    CourseStatistic,
    TeacherPerformance,
    HeadReportLog
)

@admin.register(TeacherCourseAssignment)
class TeacherCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "course", "semester", "year", "is_active")
    list_filter = ("year", "semester", "is_active", "teacher__department")
    search_fields = ("teacher__user__first_name", "teacher__user__last_name", "course__code", "course__name")
    ordering = ("-year", "semester")
    autocomplete_fields = ("teacher", "course")



# ---------------------------
# 📊 Department Statistic
# ---------------------------
@admin.register(DepartmentStatistic)
class DepartmentStatisticAdmin(admin.ModelAdmin):
    list_display = ("department", "total_students", "total_teachers", "total_courses", "success_rate", "updated_at")
    search_fields = ("department__name",)
    list_filter = ("department",)
    ordering = ("department",)



# ---------------------------
# 📚 Course Statistics Admin
# ---------------------------
@admin.register(CourseStatistic)
class CourseStatisticAdmin(admin.ModelAdmin):
    list_display = (
        "course",
        "department",
        "semester",
        "avg_score",
        "pass_rate",
        "fail_rate",
        "total_students",
        "updated_at"
    )
    list_filter = ("department", "semester")
    search_fields = ("course__code", "course__name")
    ordering = ("department", "course", "semester")
    autocomplete_fields = ("course", "department")



# ---------------------------
# ⭐ Teacher Performance Admin
# ---------------------------
@admin.register(TeacherPerformance)
class TeacherPerformanceAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "course",
        "semester",
        "year",
        "avg_success_rate",
        "avg_attendance_rate",
        "student_feedback_score",
        "updated_at"
    )
    list_filter = ("year", "semester", "teacher__department")
    search_fields = ("teacher__user__first_name", "teacher__user__last_name", "course__code", "course__name")
    ordering = ("-year", "semester")
    autocomplete_fields = ("teacher", "course")



# ---------------------------
# 🧾 Report Log Admin
# ---------------------------
@admin.register(HeadReportLog)
class HeadReportLogAdmin(admin.ModelAdmin):
    list_display = ("report_type", "department", "generated_by", "created_at")
    list_filter = ("report_type", "department")
    search_fields = ("report_type", "department__name", "generated_by__username")
    ordering = ("-created_at",)
"""