from django.contrib import admin
from .models import (
    Course,
    CourseOffering,
    CourseSchedule,
    CourseContent,
    CourseAssessmentComponent,
    Enrollment,
    CourseAttendance
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
    autocomplete_fields = ("course", "instructors")


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
    list_display = ("course", "type", "weight")
    list_filter = ("type", "course")
    search_fields = ("course__code", "course__name", "type")



@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    list_display = ('student', 'offering', 'status', 'enrolled_at')
    list_filter = ('status', 'offering')
    search_fields = ('student__email', 'offering__course__code')
    autocomplete_fields = ("student", "offering")


@admin.register(CourseAttendance)
class CourseAttendanceAdmin(admin.ModelAdmin):
    list_display = (
        "get_student",
        "get_course",
        "get_day",
        "get_time",
        "attended",
        "recorded_at",
    )

    list_filter = (
        "schedule__offering__course",
        "attended",
        "schedule__day",
    )

    search_fields = (
        "enrollment__student__user__first_name",
        "enrollment__student__user__last_name",
        "enrollment__student__student_no",
    )

    autocomplete_fields = ("enrollment", "schedule")

    def get_student(self, obj):
        return obj.enrollment.student.full_name
    get_student.short_description = "Öğrenci"

    def get_course(self, obj):
        return obj.schedule.offering.course.name
    get_course.short_description = "Ders"

    def get_day(self, obj):
        return obj.schedule.get_day_display()
    get_day.short_description = "Gün"

    def get_time(self, obj):
        return f"{obj.schedule.start_time} - {obj.schedule.end_time}"
    get_time.short_description = "Saat"