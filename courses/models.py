from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from departments.models import Department
from academics.models import Level  # senin sisteminde ayrı app'ten geldiği için

User = get_user_model()


# Fakülte modeli opsiyonel, Departments içinde olabilir ama ileride gerekirse kullanılabilir
class Faculty(models.Model):
    name = models.CharField(max_length=200, unique=True)
    code = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ("POOL", "Havuz Dersi"),
        ("FACULTY", "Fakülte Dersi"),
        ("DEPARTMENT", "Bölüm Dersi"),
    ]

    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    department = models.ManyToManyField(Department, related_name="courses", blank=True)
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name="courses")
    credit = models.FloatField(null=True, blank=True)
    ects = models.FloatField(null=True, blank=True, verbose_name="AKTS")
    course_type = models.CharField(
        max_length=20,
        choices=COURSE_TYPE_CHOICES,
        verbose_name="Ders Türü"
    )

    prerequisites = models.ManyToManyField(
        "self",
        symmetrical=False,
        blank=True,
        related_name="required_for",
        verbose_name="Önşartlı Dersler"
    )

    def __str__(self):
        return f"{self.code} - {self.name} ({self.get_course_type_display()})"

    def clean(self):
        # Kendini önkoşul olarak eklemeyi engelle
        if self.pk and self.prerequisites.filter(pk=self.pk).exists():
            raise ValidationError(_("Bir ders kendisini önkoşul olarak içeremez."))


class Teacher(models.Model):
    TEACHER_TYPE_CHOICES = [
        ("FACULTY", "Fakülte Hocası"),
        ("DEPARTMENT", "Bölüm Hocası"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="teacher_profile")
    title = models.CharField(max_length=120, blank=True)
    teacher_type = models.CharField(max_length=20, choices=TEACHER_TYPE_CHOICES, default="DEPARTMENT")
    departments = models.ManyToManyField(Department, blank=True, related_name="course_teachers")

    def __str__(self):
        return f"{self.title + ' ' if self.title else ''}{self.user.get_full_name() or self.user.username}"

class CourseOffering(models.Model):
    """
    Belirli bir dönemde açılan ders (şube).
    Kontenjan, öğretmenler, ve ders programı bu modele bağlı.
    """
    SEMESTER_CHOICES = [
        ("SPRING", "Bahar"),
        ("FALL", "Güz"),
        ("SUMMER", "Yaz"),
        ("WINTER", "Kış"),
    ]

    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="offerings")
    year = models.PositiveSmallIntegerField()
    semester = models.CharField(max_length=10, choices=SEMESTER_CHOICES)
    section = models.CharField(max_length=10, blank=True, help_text="Şube kodu (örn: A, B, 01)")
    instructors = models.ManyToManyField(Teacher, related_name="offerings", blank=True)
    max_students = models.PositiveIntegerField(default=30, verbose_name="Kontenjan")
    location = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.course.code}-{self.section or '1'} ({self.semester} {self.year})"

    @property
    def enrolled_count(self):
        return self.enrollments.filter(status=Enrollment.Status.ENROLLED).count()

    def clean(self):
        if self.max_students <= 0:
            raise ValidationError({"max_students": _("Kontenjan pozitif olmalıdır.")})


class DayOfWeek(models.TextChoices):
    MON = "MON", _("Pazartesi")
    TUE = "TUE", _("Salı")
    WED = "WED", _("Çarşamba")
    THU = "THU", _("Perşembe")
    FRI = "FRI", _("Cuma")
    SAT = "SAT", _("Cumartesi")
    SUN = "SUN", _("Pazar")


class CourseSchedule(models.Model):
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="schedules")
    day = models.CharField(max_length=3, choices=DayOfWeek.choices)
    start_time = models.TimeField()
    end_time = models.TimeField()
    place = models.CharField(max_length=200, blank=True)

    class Meta:
        ordering = ["day", "start_time"]

    def clean(self):
        if self.end_time <= self.start_time:
            raise ValidationError({"end_time": _("Bitiş saati başlangıçtan sonra olmalıdır.")})

    def __str__(self):
        return f"{self.get_day_display()} {self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')}"


class CourseContent(models.Model):
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="contents")
    week = models.PositiveIntegerField(null=True, blank=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resources = models.TextField(blank=True, help_text="Ders notları / bağlantılar")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("week", "created_at")

    def __str__(self):
        return f"{self.offering.course.code} - {self.title}"


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "ENROLLED", _("Kayıtlı")
        WAITLISTED = "WAITLISTED", _("Yedek")
        DROPPED = "DROPPED", _("Bırakıldı")
        COMPLETED = "COMPLETED", _("Tamamlandı")

    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name="enrollments")
    offering = models.ForeignKey(CourseOffering, on_delete=models.CASCADE, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ENROLLED)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("student", "offering")

    def clean(self):
        if self.status == Enrollment.Status.ENROLLED and self.offering.enrolled_count >= self.offering.max_students:
            raise ValidationError(_("Kontenjan dolu, öğrenci yedek listesine alınmalı."))

    def __str__(self):
        return f"{self.student} -> {self.offering} ({self.get_status_display()})"
