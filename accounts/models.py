from django.db import models

class SimpleUser(models.Model):
    class Roles(models.TextChoices):
        STUDENT = "STUDENT", "Öğrenci"
        TEACHER = "TEACHER", "Öğretmen"
        HOD     = "HOD", "Bölüm Başkanı"
        DEAN    = "DEAN", "Dekan"

    # GİRİŞ İÇİN KULLANILAN KULLANICI ADI
    username = models.CharField(max_length=150, unique=True)

    # İSİM – SOYİSİM (EKLEDİK)
    first_name = models.CharField(max_length=50, blank=True)
    last_name  = models.CharField(max_length=50, blank=True)

    password = models.CharField(max_length=128)
    role     = models.CharField(max_length=20, choices=Roles.choices)
    email    = models.EmailField(unique=True, blank=True, null=True)

    def get_full_name(self):
        # Eğer ad/soyad doldurulmuşsa onları kullan
        full = f"{self.first_name} {self.last_name}".strip()
        if full:
            return full
        # Doldurulmadıysa geriye username kalsın (eski davranış)
        return self.username

    def __str__(self):
        # Admin vs için de tam isim kullanmak güzel olur
        return f"{self.get_full_name()} ({self.role})"
