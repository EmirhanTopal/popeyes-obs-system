from django.db import models

class Department(models.Model):
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100)
    faculty = models.ForeignKey('faculty.Faculty', on_delete=models.CASCADE, related_name="departments")

    def __str__(self):
        return f"{self.code} - {self.name}"


