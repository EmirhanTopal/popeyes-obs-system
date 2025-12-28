from django.contrib import admin
from .models import (
    Head,
    TeacherCourseAssignment,
    CourseStatistic,
    TeacherPerformance,
    HeadReportLog
)


@admin.register(Head)
class HeadAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "department",
        "is_active",
        "start_date",
        "end_date",
    )

    search_fields = (
        "teacher__user__username",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "department__name",
    )

    list_filter = (
        "is_active",
        "department",
    )

    ordering = ("department",)

    autocomplete_fields = ("teacher", "department")

    fieldsets = (
        ("Bölüm Başkanı Bilgisi", {
            "fields": ("teacher", "department")
        }),
        ("Görev Bilgileri", {
            "fields": ("is_active", "start_date", "end_date")
        }),
    )

    readonly_fields = ("start_date",)
