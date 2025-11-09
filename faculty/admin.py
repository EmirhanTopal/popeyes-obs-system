from django.contrib import admin
from faculty.models import Faculty

# Register your models here.
@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'dean_name')
    search_fields = ('dean_name',)