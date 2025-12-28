from departments.models import Department
from academics.models import Level
from django.db import models
from teachers.models import Teacher
from accounts.models import SimpleUser
from courses.models import Course, CourseOffering

class Student(models.Model):
    user = models.OneToOneField(SimpleUser, on_delete=models.CASCADE)

    student_no = models.CharField(max_length=10, unique=True)

    departments = models.ManyToManyField(
        Department,
        related_name="students",
        blank=True
    )

    advisor = models.ForeignKey(
        Teacher,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="advisees"
    )

    student_level = models.ForeignKey(
        Level,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="students"
    )

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.student_no}"

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email
