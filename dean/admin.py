from django.contrib import admin
from .models import Dean, FacultySettings, FacultyReport


@admin.register(Dean)
class DeanAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "faculty",
        "teacher_full_name",
    )

    search_fields = (
        "teacher__user__username",
        "teacher__user__first_name",
        "teacher__user__last_name",
        "faculty__name",
    )

    autocomplete_fields = ("teacher", "faculty")
    
    def teacher_full_name(self, obj):
        return obj.teacher.full_name if obj.teacher else "-"
    teacher_full_name.short_description = "Dean"


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
