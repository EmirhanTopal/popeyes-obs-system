from django.contrib import admin
from .models import SimpleUser

from students.models import Student
from teachers.models import Teacher

class StudentInline(admin.StackedInline):
    model = Student
    extra = 0

class TeacherInline(admin.StackedInline):
    model = Teacher
    extra = 0

@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ("username", "role")
    search_fields = ("username", "first_name", "last_name")
    inlines = [StudentInline, TeacherInline]

