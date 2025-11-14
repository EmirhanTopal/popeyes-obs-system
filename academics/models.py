from django.db import models
from django.db import migrations, models

class Level(models.Model):
    number = models.PositiveSmallIntegerField(unique=True)  # 1,2,3,4
    name = models.CharField(max_length=50)                  # “1. Sınıf” gibi

    def __str__(self):
        return self.name
