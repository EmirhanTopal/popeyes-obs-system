from django.db import models

class ProgramOutcome(models.Model):
    PROGRAM_CHOICES = [
        ('computer', 'Bilgisayar Mühendisliği'),
        ('biomedical', 'Biyomedikal Mühendisliği'),
    ]
    
    program = models.CharField(max_length=20, choices=PROGRAM_CHOICES)
    outcome_number = models.IntegerField()
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['program', 'outcome_number']
    
    def __str__(self):
        return f"{self.get_program_display()} - Outcome {self.outcome_number}"