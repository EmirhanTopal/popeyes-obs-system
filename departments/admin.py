from django.contrib import admin
from departments.models import Department

# Register your models here.
@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'faculty')
    list_filter = ('faculty',)
    search_fields = ('code', 'name')

