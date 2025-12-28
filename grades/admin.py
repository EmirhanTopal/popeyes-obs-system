from urllib import request
from django.contrib import admin
from .models import Grade, GradeComponent, LetterGradeScale


# ================================
# INLINE — GradeComponent
# ================================
class GradeComponentInline(admin.TabularInline):
    model = GradeComponent
    extra = 0
    autocomplete_fields = ["component"]  # CourseAssessmentComponent seçimi kolay olsun
    fields = ["component", "score"]
    readonly_fields = []


# ================================
# GRADE ADMIN
# ================================
@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    list_display = (
        "student",
        "offering",
        "total_score",
        "letter_grade",
        "gpa_value",
        "updated_at"
    )

    list_filter = ("offering__course__code", "letter_grade")
    search_fields = ("student__username", "student__full_name", "offering__course__code")

    inlines = [GradeComponentInline]

    readonly_fields = ("total_score", "letter_grade", "gpa_value")

    fieldsets = (
        ("Öğrenci ve Ders", {
            "fields": ("student", "offering")
        }),
        ("Hesaplanan Notlar", {
            "fields": ("total_score", "letter_grade", "gpa_value")
        }),
    )

    def save_related(self, request, form, formsets, change):
        super().save_related(request, form, formsets, change)
        form.instance.save()


# ================================
# LETTER GRADE SCALE ADMIN
# ================================
@admin.register(LetterGradeScale)
class LetterGradeScaleAdmin(admin.ModelAdmin):
    list_display = ("letter", "min_score", "max_score", "gpa_value")
    list_editable = ("min_score", "max_score", "gpa_value")
    ordering = ("-gpa_value",)
    search_fields = ("letter",)
    list_filter = ("gpa_value",)


# ================================
# GRADE COMPONENT ADMIN
# ================================
@admin.register(GradeComponent)
class GradeComponentAdmin(admin.ModelAdmin):
    list_display = ("grade", "component", "score")
    search_fields = ("grade__student__username", "component__type")
    list_filter = ("component__type",)


