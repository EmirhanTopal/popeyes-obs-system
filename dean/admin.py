from django.contrib import admin
from .models import Dean, FacultySettings, FacultyReport


@admin.register(Dean)
class DeanAdmin(admin.ModelAdmin):
    list_display = ("user", "faculty", "full_name")
    search_fields = ("user__username", "faculty__name", "full_name")


@admin.register(FacultySettings)
class FacultySettingsAdmin(admin.ModelAdmin):
    list_display = (
        "faculty",
        "max_students_per_class",
        "max_courses_per_student",
        "grading_system",
        "updated_at",
    )
    search_fields = ("faculty__name",)


@admin.register(FacultyReport)
class FacultyReportAdmin(admin.ModelAdmin):
    list_display = (
        "faculty",
        "semester",
        "average_gpa",
        "total_students",
        "total_teachers",
        "created_at",
    )
    list_filter = ("semester", "faculty")
