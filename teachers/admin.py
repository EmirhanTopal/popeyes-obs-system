from django.contrib import admin
from .models import Teacher, TeacherSchedule, OfficeHour
from hod.models import Head
from dean.models import Dean



class HeadInline(admin.StackedInline):
    model = Head
    extra = 0
    autocomplete_fields = ("department",)


class DeanInline(admin.StackedInline):
    model = Dean
    extra = 0
    autocomplete_fields = ("faculty",)



# =====================================================
# INLINE MODELLER
# =====================================================

class TeacherScheduleInline(admin.TabularInline):
    model = TeacherSchedule
    extra = 1
    fields = ("day_of_week", "start_time", "end_time", "location", "activity_type")
    ordering = ("day_of_week", "start_time")
    show_change_link = True


class OfficeHourInline(admin.TabularInline):
    model = OfficeHour
    extra = 1
    fields = ("day_of_week", "start_time", "end_time", "is_active")
    ordering = ("day_of_week", "start_time")
    show_change_link = True


# =====================================================
# TEACHER ADMIN
# =====================================================

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = (
        "full_name",
        "academic_title",
        "department",
        "teacher_type",
        "is_active",
        "created_at",
    )

    list_filter = (
        "department",
        "teacher_type",
        "academic_title",
        "is_active",
    )

    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "department__name",
    )

    ordering = ("department", "user__username")

    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        ("Kimlik Bilgileri", {
            "fields": ("user", "department", "teacher_type", "academic_title")
        }),
        ("Uzmanlık ve Ofis Bilgileri", {
            "fields": ("expertise_area", "office_location", "office_phone")
        }),
        ("İletişim Bilgileri", {
            "fields": ("personal_website", "linkedin", "google_scholar", "researchgate", "orcid")
        }),
        ("Durum", {
            "fields": ("is_active", "created_at", "updated_at")
        }),
    )

    inlines = [
        HeadInline,
        DeanInline,
        TeacherScheduleInline,
        OfficeHourInline,
    ]

    autocomplete_fields = ("user", "department")


# =====================================================
# TEACHER SCHEDULE ADMIN
# =====================================================

@admin.register(TeacherSchedule)
class TeacherScheduleAdmin(admin.ModelAdmin):
    list_display = (
        "teacher",
        "day_of_week",
        "start_time",
        "end_time",
        "location",
        "activity_type"
    )

    list_filter = ("day_of_week", "teacher__department")
    search_fields = ("teacher__user__username",)
    ordering = ("day_of_week", "start_time")

    autocomplete_fields = ("teacher",)


# =====================================================
# OFFICE HOUR ADMIN
# =====================================================

@admin.register(OfficeHour)
class OfficeHourAdmin(admin.ModelAdmin):
    list_display = ("teacher", "day_of_week", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active", "teacher__department")
    search_fields = ("teacher__user__username",)
    ordering = ("day_of_week", "start_time")

    autocomplete_fields = ("teacher",)
