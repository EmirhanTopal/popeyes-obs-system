from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import SimpleUser
from courses.models import CourseOffering, CourseAssessmentComponent
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

 
# ============================================================
# GRADE MODEL (ANA TABLO)
# ============================================================
class Grade(models.Model):
    """
    Bir öğrencinin bir şubedeki notlarını tutar.
    Artık NOTLAR DİNAMİK, bileşenler GradeComponent tablosunda tutulur.
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

    # Hesaplanan bilgiler
    total_score = models.FloatField(null=True, blank=True)
    letter_grade = models.CharField(max_length=2, null=True, blank=True)
    gpa_value = models.FloatField(null=True, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("student", "offering")
        verbose_name = "Not"
        verbose_name_plural = "Notlar"

    # ========================
    # DİNAMİK NOT HESAPLAMA
    # ========================
    def calculate_total(self):
        components = self.component_grades.select_related("component")

        if not components.exists():
            return None

        total = 0

        for c in components:
            if c.score is None:
                return None  # tüm bileşenler girilmemişse hesaplama yok

            weight = c.component.weight / 100
            total += c.score * weight

        return round(total, 2)

    def assign_letter_grade(self):
        """Harf notu bulma"""
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
        super().save(*args, **kwargs)


    def __str__(self):
        return f"{self.student} → {self.offering} ({self.letter_grade})"


# ============================================================
# DİNAMİK NOT TABLOSU (Vize, Final, Quiz, Proje vs)
# ============================================================
class GradeComponent(models.Model):
    grade = models.ForeignKey(
        Grade,
        on_delete=models.CASCADE,
        related_name="component_grades"
    )

    component = models.ForeignKey(
        CourseAssessmentComponent,
        on_delete=models.CASCADE
    )

    score = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("grade", "component")

    def clean(self):
        if self.component.offering != self.grade.offering:
            raise ValidationError(
                "Bu bileşen, bu dersin değerlendirme sistemine ait değil."
            )
        
    


    def __str__(self):
        return f"{self.grade.student} - {self.component.get_type_display()} : {self.score}"


# ============================================================
# HARF NOTU TABLOSU (AA-FF)
# ============================================================
class LetterGradeScale(models.Model):

    letter = models.CharField(max_length=2, unique=True)
    min_score = models.FloatField()
    max_score = models.FloatField()
    gpa_value = models.FloatField(help_text="4.0 sistemi katsayısı")

    class Meta:
        ordering = ["-gpa_value"]

    def __str__(self):
        return f"{self.letter} ({self.min_score}-{self.max_score})"


# ============================================================
# TRANSCRIPT / GPA HESAPLAYICI
# ============================================================
class TranscriptManager:

    @staticmethod
    def calculate_gpa(student):
        grades = Grade.objects.filter(
            student=student,
            letter_grade__isnull=False
        )

        if not grades.exists():
            return 0.0

        total_points = 0
        total_credits = 0

        for g in grades:
            credit = g.offering.course.credit
            total_points += g.gpa_value * credit
            total_credits += credit

        return round(total_points / total_credits, 2)


    @staticmethod
    def semester_grades(student, year, semester):
        return Grade.objects.filter(
            student=student,
            offering__year=year,
            offering__semester=semester
        )

    @staticmethod
    def course_statistics(offering):
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

@receiver([post_save, post_delete], sender=GradeComponent)
def recalc_grade(sender, instance, **kwargs):
    grade = instance.grade
    grade.total_score = grade.calculate_total()
    if grade.total_score is not None:
        grade.letter_grade, grade.gpa_value = grade.assign_letter_grade()
    else:
        grade.letter_grade = None
        grade.gpa_value = None
    grade.save(update_fields=["total_score", "letter_grade", "gpa_value"])

