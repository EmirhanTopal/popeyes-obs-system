from django.contrib import admin
from .models import (
    Course,
    CourseOffering,
    CourseSchedule,
    CourseContent,
    CourseAssessmentComponent,
    Enrollment
)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'level', 'course_type')
    list_filter = ('course_type', 'level')
    search_fields = ('code', 'name')


@admin.register(CourseOffering)
class CourseOfferingAdmin(admin.ModelAdmin):
    list_display = ('course', 'section', 'semester', 'year', 'max_students')
    list_filter = ('semester', 'year')
    search_fields = ('course__code', 'course__name')


@admin.register(CourseSchedule)
class CourseScheduleAdmin(admin.ModelAdmin):
    list_display = ('offering', 'day', 'start_time', 'end_time', 'place')
    list_filter = ('day',)
    search_fields = ('offering__course__code', 'offering__course__name')


@admin.register(CourseContent)
class CourseContentAdmin(admin.ModelAdmin):
    list_display = ('offering', 'week', 'title', 'created_at')
    list_filter = ('week',)
    search_fields = ('offering__course__code', 'title')


@admin.register(CourseAssessmentComponent)
class CourseAssessmentComponentAdmin(admin.ModelAdmin):
    list_display = ('course', 'name', 'weight')
    list_filter = ('course',)
    search_fields = ('course__code', 'name')


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'offering', 'status', 'enrolled_at')
    list_filter = ('status', 'offering')
    search_fields = ('student__email', 'offering__course__code')
