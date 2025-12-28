from django.contrib import admin
from .models import Student

# ============================================================
# Student Admin
# ============================================================
@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ['student_no', 'full_name', 'email', 'advisor_display', 'level_display']
    search_fields = ['student_no', 'user__first_name', 'user__last_name', 'user__email']
    list_filter = ['student_level']

    def advisor_display(self, obj):
        return obj.advisor.full_name if obj.advisor else "-"
    advisor_display.short_description = "Danışman"

    def level_display(self, obj):
        return obj.student_level.name if obj.student_level else "-"
    level_display.short_description = "Seviye"




