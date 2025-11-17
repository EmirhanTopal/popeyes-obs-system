from departments.models import Department
from academics.models import Level
from django.db import models
from teachers.models import Teacher
from accounts.models import SimpleUser
from courses.models import CourseOffering

class Student(models.Model):
    user = models.OneToOneField(SimpleUser, on_delete=models.CASCADE)

    student_no = models.CharField(max_length=10, unique=True)

    departments = models.ManyToManyField(Department, related_name="students", blank=True)

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

class StudentCourseEnrollment(models.Model):
    ENROLLMENT_TYPES = [
        ('REQUIRED', 'Zorunlu'),
        ('ELECTIVE', 'Seçmeli'),
    ]

    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name='student_enrollments')

    enrollment_type = models.CharField(max_length=20, choices=ENROLLMENT_TYPES, default='REQUIRED')
    is_active = models.BooleanField(default=True)

    enrolled_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.student.full_name} → {self.course.code}"


class CourseAttendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendance_records')
    course = models.ForeignKey("courses.Course", on_delete=models.CASCADE, related_name='attendance_records')

    date = models.DateField()
    hours_missed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.student.full_name} - {self.course.code} ({self.date})"

