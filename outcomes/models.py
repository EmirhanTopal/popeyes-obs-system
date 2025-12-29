from django.db import models
from departments.models import Department
from courses.models import CourseOffering

class ProgramOutcome(models.Model):
    department = models.ForeignKey(
        Department,
        on_delete=models.CASCADE,
        related_name="program_outcomes",
        verbose_name="Program / Bölüm"
    )
    code = models.IntegerField()
    description = models.TextField()

    class Meta:
        unique_together = ['department', 'code']

    def __str__(self):
        short_desc = self.description[:80] + "..." if len(self.description) > 80 else self.description
        return f"{self.code} - {short_desc}"


# ============================================================
# LEARNING OUTCOME
# ============================================================
class LearningOutcome(models.Model):

    BLOOM_LEVELS = [
        ("REMEMBER", "Remember"),
        ("UNDERSTAND", "Understand"),
        ("APPLY", "Apply"),
        ("ANALYZE", "Analyze"),
        ("EVALUATE", "Evaluate"),
        ("CREATE", "Create"),
    ]

    course = models.ForeignKey(
        "courses.Course",
        on_delete=models.CASCADE,
        related_name="learning_outcomes"
    )

    code = models.CharField(
        max_length=20,
        verbose_name="Kodu (ör: LO1)"
    )

    description = models.TextField(
        verbose_name="Açıklama"
    )

    bloom_level = models.CharField(
        max_length=20,
        choices=BLOOM_LEVELS,
        default="REMEMBER"
    )

    order = models.PositiveIntegerField(
        default=1
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.course.code} - {self.code}"


# ============================================================
# STUDENT PROGRAM OUTCOME SCORE
# ============================================================
class StudentProgramOutcomeScore(models.Model):
    """
    Her öğrencinin kendi Program Outcome skorlarını tutar.
    Aynı ProgramOutcome için her öğrencinin farklı bir satırı olur.
    """
    student = models.ForeignKey(
        "students.Student",  # ✅ Lazy reference — circular import çözümü
        on_delete=models.CASCADE,
        related_name="program_scores"
    )
    program_outcome = models.ForeignKey(ProgramOutcome, on_delete=models.CASCADE)
    score = models.FloatField(default=0.0)
    coverage = models.FloatField(default=0.0)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('student', 'program_outcome')

    def __str__(self):
        return f"{self.student} → {self.program_outcome.code}: {self.score:.2f}"
