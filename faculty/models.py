from django.db import models

class Faculty(models.Model):
    full_name = models.CharField(max_length=100)
    dean_name = models.ForeignKey(
        'dean.Dean',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='faculties'
    )

    def __str__(self):
        return self.full_name
