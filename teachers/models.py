from django.db import models

from departments.models import Department


class Teacher(models.Model):
    full_name = models.CharField(max_length=100)
    department = models.ManyToManyField(Department, related_name="teachers")
    #advisor eklendi in student
    def __str__(self):
        return f"{self.full_name}"
