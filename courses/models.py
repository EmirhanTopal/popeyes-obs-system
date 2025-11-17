from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import SimpleUser
from academics.models import Level


# ============================================================
# COURSE MODEL
# ============================================================
class Course(models.Model):
    STATUS_CHOICES = [
        ("PENDING", "Onay Bekliyor"),
        ("APPROVED", "Onaylandı"),
        ("REJECTED", "Reddedildi"),
    ]

    COURSE_TYPE_CHOICES = [
        ("POOL", "Havuz Dersi"),
        ("FACULTY", "Fakülte Dersi"),
        ("DEPARTMENT", "Bölüm Dersi"),
    ]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)

    level = models.ForeignKey(
        Level,
        on_delete=models.CASCADE,
        related_name="courses",
    )

    credit = models.FloatField(null=True, blank=True)
    ects = models.FloatField(null=True, blank=True, verbose_name="AKTS")
    is_active = models.BooleanField(default=True)

    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        verbose_name="Ders Türü",
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING",
    )
    semester = models.PositiveSmallIntegerField(default=1, verbose_name="Dönem")

    # Head hangi bölüm için oluşturmuş?
    created_by_head = models.ForeignKey(
        "hod.Head",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )

    # Öğretmen – Ders ilişkisi
    teachers = models.ManyToManyField(
        "teachers.Teacher",
        related_name="courses",
        blank=True,
    )

    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="required_for",
        verbose_name="Önşartlı Dersler",
    )

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_course_type_display()})"

    def clean(self):
        super().clean()

        # Kendini kendine önkoşul yapma
        if self.pk and self.prerequisites.filter(pk=self.pk).exists():
            raise ValidationError(_("Bir ders kendisini önkoşul olarak içeremez."))


# ============================================================
# COURSE COMPONENTS
# ============================================================
class CourseAssessmentComponent(models.Model):
    COMPONENT_TYPES = [
        ("MIDTERM", "Vize"),
        ("FINAL", "Final"),
        ("ASSIGNMENT", "Ödev"),
        ("ATTENDANCE", "Devam"),
        ("QUIZ", "Quiz"),
        ("PROJECT", "Proje"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="components",
    )

    type = models.CharField(max_length=20, choices=COMPONENT_TYPES)
    weight = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["course", "type"]

    def __str__(self):
        return f"{self.course.code} - {self.get_type_display()} (%{self.weight})"


# ============================================================
# COURSE OFFERING (Şube)
# ============================================================
class CourseOffering(models.Model):
    SEMESTER_CHOICES = [
        ("SPRING", "Bahar"),
        ("FALL", "Güz"),
        ("SUMMER", "Yaz"),
        ("WINTER", "Kış"),
    ]

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="offerings",
    )
    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)

    section = models.CharField(max_length=10, blank=True)

    instructors = models.ManyToManyField(
        "teachers.Teacher",
        related_name="offerings",
        blank=True,
    )

    max_students = models.PositiveIntegerField(
        default=30,
        verbose_name="Kontenjan",
    )
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.course.code}-{self.section or '1'} ({self.semester} {self.year})"

    @property
    def enrolled_count(self):
        from .models import Enrollment  # dairesel importtan kaçınmak için lokal import
        return self.enrollments.filter(
            status=Enrollment.Status.ENROLLED
        ).count()

    def clean(self):
        if self.max_students <= 0:
            raise ValidationError(
                {"max_students": _("Kontenjan pozitif olmalıdır.")}
            )


# ============================================================
# COURSE SCHEDULE
# ============================================================
class DayOfWeek(models.TextChoices):
    MON = "MON", _("Pazartesi")
    TUE = "TUE", _("Salı")
    WED = "WED", _("Çarşamba")
    THU = "THU", _("Perşembe")
    FRI = "FRI", _("Cuma")
    SAT = "SAT", _("Cumartesi")
    SUN = "SUN", _("Pazar")


class CourseSchedule(models.Model):
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="schedules",
    )
    day = models.CharField(max_length=3, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    place = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["day", "start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError(
                {"end_time": _("Bitiş saati başlangıçtan sonra olmalıdır.")}
            )

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time} - {self.end_time}"


# ============================================================
# COURSE CONTENT
# ============================================================
class CourseContent(models.Model):
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="contents",
    )
    week = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resources = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("week", "created_at")

    def __str__(self):
        return f"{self.offering.course.code} - {self.title}"


# ============================================================
# ENROLLMENT
# ============================================================
class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", _("Kayıtlı")
        WAITLISTED = "WAITLISTED", _("Yedek")
        DROPPED = "DROPPED", _("Bırakıldı")
        COMPLETED = "COMPLETED", _("Tamamlandı")

    student = models.ForeignKey(
        SimpleUser,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="enrollments",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.ENROLLED,
    )
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "offering")

    def clean(self):
        if (
            self.status == Enrollment.Status.ENROLLED
            and self.offering.enrolled_count >= self.offering.max_students
        ):
            raise ValidationError(
                _("Kontenjan dolu, öğrenci yedek listesine alınmalı.")
            )

    def __str__(self):
        return f"{self.student} -> {self.offering} ({self.get_status_display()})"


# ============================================================
# COURSE ATTENDANCE
# ============================================================
class CourseAttendance(models.Model):
    enrollment = models.ForeignKey(
        Enrollment,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    schedule = models.ForeignKey(
        CourseSchedule,
        on_delete=models.CASCADE,
        related_name="attendances",
    )
    attended = models.BooleanField(default=False, verbose_name="Katıldı")
    note = models.CharField(max_length=255, blank=True, verbose_name="Not")
    recorded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("enrollment", "schedule")
        ordering = ["schedule__day", "schedule__start_time"]

    def __str__(self):
        status = "Katıldı" if self.attended else "Katılmadı"
        return f"{self.enrollment.student} - {self.schedule} ({status})"
