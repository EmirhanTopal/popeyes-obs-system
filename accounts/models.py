from django.db import models

class SimpleUser(models.Model):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Öğrenci"
        TEACHER = "TEACHER", "Öğretmen"
        HOD     = "HOD", "Bölüm Başkanı"
        DEAN    = "DEAN", "Dekan"

    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # basitlik için düz metin (demo!)
    role     = models.CharField(max_length=20, choices=Roles.choices)

    def __str__(self):
        return f"{self.username} ({self.role})"
