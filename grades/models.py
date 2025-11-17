from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from accounts.models import SimpleUser
from courses.models import CourseOffering


# ============================================================
# HARF NOTU TABLOSU
# ============================================================
class LetterGradeScale(models.Model):
    """
    Yönetici panelinden düzenlenebilir harf notu ölçeği.
    Örnek:
        AA: 90 - 100 → 4.0
        BA: 85 - 89  → 3.5
    """

    letter = models.CharField(max_length=2, unique=True)
    min_score = models.FloatField()
    max_score = models.FloatField()
    gpa_value = models.FloatField(help_text="4.0 sistemi katsayısı")

    class Meta:
        ordering = ["-gpa_value"]

    def __str__(self):
        return f"{self.letter} ({self.min_score}-{self.max_score})"



# ============================================================
# GRADES MODEL
# ============================================================
class Grade(models.Model):
    """
    Bir öğrencinin bir şubedeki notlarını tutar.
        SimpleUser + CourseOffering = Unique
    """

    student = models.ForeignKey(
        SimpleUser,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    offering = models.ForeignKey(
        CourseOffering,
        on_delete=models.CASCADE,
        related_name="grades"
    )

    # Notlar
    midterm = models.FloatField(null=True, blank=True, verbose_name="Vize")
    final = models.FloatField(null=True, blank=True, verbose_name="Final")
    makeup = models.FloatField(null=True, blank=True, verbose_name="Bütünleme")

    # Hesaplanmış alanlar
    total_score = models.FloatField(null=True, blank=True)
    letter_grade = models.CharField(max_length=2, null=True, blank=True)
    gpa_value = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "offering")  # aynı öğrenci aynı dersi 1 kez alır
        verbose_name = "Not"
        verbose_name_plural = "Notlar"

    # ============================================================
    # HESAPLAMALAR
    # ============================================================

    def calculate_total(self):
        """Vize %40, Final/Bütünleme %60"""
        if self.midterm is None:
            return None

        exam = self.makeup if self.makeup is not None else self.final
        if exam is None:
            return None

        return round(self.midterm * 0.40 + exam * 0.60, 2)

    def assign_letter_grade(self):
        """LetterGradeScale tablosundan uygun harf notunu bulur."""
        if self.total_score is None:
            return None, None

        scale = LetterGradeScale.objects.filter(
            min_score__lte=self.total_score,
            max_score__gte=self.total_score
        ).first()

        if scale:
            return scale.letter, scale.gpa_value

        return "FF", 0.0

    def save(self, *args, **kwargs):
        self.total_score = self.calculate_total()

        if self.total_score is not None:
            self.letter_grade, self.gpa_value = self.assign_letter_grade()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student} -> {self.offering}: {self.letter_grade}"


# ============================================================
# TRANSCRIPT / GPA YARDIMCI SINIFI
# ============================================================
class TranscriptManager:

    @staticmethod
    def calculate_gpa(student):
        """Öğrenci genel GPA."""
        grades = Grade.objects.filter(
            student=student,
            letter_grade__isnull=False
        )

        if not grades.exists():
            return 0.0

        gpa = sum(g.gpa_value for g in grades) / grades.count()
        return round(gpa, 2)

    @staticmethod
    def semester_grades(student, year, semester):
        """Belirli dönem not dökümü."""
        return Grade.objects.filter(
            student=student,
            offering__year=year,
            offering__semester=semester
        )

    @staticmethod
    def course_statistics(offering):
        """Şube bazlı istatistikler."""
        grades = Grade.objects.filter(
            offering=offering,
            total_score__isnull=False
        )

        if not grades:
            return {}

        scores = [g.total_score for g in grades]

        return {
            "ortalama": round(sum(scores) / len(scores), 2),
            "min": min(scores),
            "max": max(scores),
            "geçen_sayısı": grades.filter(gpa_value__gt=0).count(),
            "kalan_sayısı": grades.filter(gpa_value=0).count(),
        }
