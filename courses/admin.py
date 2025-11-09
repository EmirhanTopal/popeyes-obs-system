from django.contrib import admin
from courses.models import Course
# Register your models here.
@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'course_type')
    list_filter = ('course_type', 'level')
    search_fields = ('code', 'name')