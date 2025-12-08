from django.db import models
from departments.models import Department
from accounts.models import SimpleUser

class Teacher(models.Model):
    TEACHER_TYPES = [
        ('FACULTY', 'Fakülte Hocası'),
        ('DEPARTMENT', 'Bölüm Hocası'),
        ('ELECTIVE', 'Seçmeli Ders Hocası'),
    ]

    ACADEMIC_TITLES = [
        ('PROF_DR', 'Prof. Dr.'),
        ('ASSOC_PROF_DR', 'Doç. Dr.'),
        ('ASSIST_PROF_DR', 'Dr. Öğr. Üyesi'),
        ('INSTRUCTOR', 'Öğr. Gör.'),
        ('RESEARCH_ASSIST', 'Arş. Gör.'),
    ]

    user = models.OneToOneField(
        SimpleUser,
        on_delete=models.CASCADE,
        related_name='teacher_profile'
    )


    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        verbose_name="Bölüm"
    )

    teacher_type = models.CharField(
        max_length=20,
        choices=TEACHER_TYPES,
        default='DEPARTMENT',
        verbose_name="Öğretmen Tipi"
    )

    academic_title = models.CharField(
        max_length=20,
        choices=ACADEMIC_TITLES,
        default='INSTRUCTOR',
        verbose_name="Akademik Unvan"
    )

    expertise_area = models.TextField(
        blank=True,
        verbose_name="Uzmanlık Alanları"
    )

    office_location = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Ofis No"
    )
    office_phone = models.CharField(
        max_length=15,
        blank=True,
        verbose_name="Ofis Telefonu"
    )

    personal_website = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)
    google_scholar = models.URLField(blank=True)
    researchgate = models.URLField(blank=True)
    orcid = models.CharField(max_length=20, blank=True)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Öğretim Görevlisi"
        verbose_name_plural = "Öğretim Görevlileri"
        ordering = ['academic_title', 'id']

    def __str__(self):
        return f"{self.get_academic_title_display()} {self.user.get_full_name()}"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email

    @property
    def has_contact_info(self):
        return any([
            self.personal_website,
            self.linkedin,
            self.google_scholar,
            self.researchgate,
            self.orcid
        ])



class TeacherSchedule(models.Model):
    DAYS_OF_WEEK = [
        ('MON', 'Pazartesi'),
        ('TUE', 'Salı'),
        ('WED', 'Çarşamba'),
        ('THU', 'Perşembe'),
        ('FRI', 'Cuma'),
        ('SAT', 'Cumartesi'),
        ('SUN', 'Pazar'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK, verbose_name="Gün")
    start_time = models.TimeField(verbose_name="Başlangıç Saati")
    end_time = models.TimeField(verbose_name="Bitiş Saati")
    location = models.CharField(max_length=100, verbose_name="Yer")
    activity_type = models.CharField(max_length=50, verbose_name="Etkinlik Türü")

    class Meta:
        verbose_name = "Öğretmen Programı"
        verbose_name_plural = "Öğretmen Programları"
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.teacher} - {self.get_day_of_week_display()} {self.start_time}"


class OfficeHour(models.Model):
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='office_hours')
    day_of_week = models.CharField(max_length=3, choices=TeacherSchedule.DAYS_OF_WEEK, verbose_name="Gün")
    start_time = models.TimeField(verbose_name="Başlangıç Saati")
    end_time = models.TimeField(verbose_name="Bitiş Saati")
    is_active = models.BooleanField(default=True, verbose_name="Aktif")

    class Meta:
        verbose_name = "Ofis Saati"
        verbose_name_plural = "Ofis Saatleri"
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.teacher} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"
