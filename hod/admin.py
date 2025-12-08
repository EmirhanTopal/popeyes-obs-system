from django.contrib import admin
from .models import Head
from .models import (
    TeacherCourseAssignment,
    CourseStatistic,
    TeacherPerformance,
    HeadReportLog
)

@admin.register(Head)
class HeadAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "department",
        "teacher_profile",
        "is_active",
        "start_date",
        "end_date",
    )

    search_fields = (
        "head_user__first_name",
        "head_user__last_name",
        "department__name",
    )

    list_filter = (
        "is_active",
        "department",
    )

    ordering = ("department",)

    autocomplete_fields = ("head_user", "department", "teacher_profile")

    fieldsets = (
        ("Bölüm Başkanı Bilgisi", {
            "fields": ("head_user", "department", "teacher_profile")
        }),
        ("Görev Bilgileri", {
            "fields": ("is_active", "start_date", "end_date")
        }),
        ("Sistem", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",)
        }),
    )

    readonly_fields = ("created_at", "updated_at", "start_date")

@admin.register(TeacherCourseAssignment)
class TeacherCourseAssignmentAdmin(admin.ModelAdmin):
    list_display = ("teacher", "course", "semester", "year", "is_active")
    list_filter = ("year", "semester", "is_active", "teacher__department")
    search_fields = ("teacher__user__first_name", "teacher__user__last_name", "course__code", "course__name")
    ordering = ("-year", "semester")
    autocomplete_fields = ("teacher", "course")

# ---------------------------
# Course Statistics Admin
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
# Teacher Performance Admin
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
# Report Log Admin
# ---------------------------
@admin.register(HeadReportLog)
class HeadReportLogAdmin(admin.ModelAdmin):
    list_display = ("report_type", "department", "generated_by", "created_at")
    list_filter = ("report_type", "department")
    search_fields = ("report_type", "department__name", "generated_by__username")
    ordering = ("-created_at",)
