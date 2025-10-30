from django.db import models

class Dean(models.Model):
    full_name = models.CharField(max_length=100, unique=True)
