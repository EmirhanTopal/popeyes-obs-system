from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import SimpleUser
from teachers.models import Teacher
from departments.models import Department, Faculty, DepartmentStatistic, DepartmentCourse
from courses.models import Course, Level
from .models import Head


class HODViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Altyapı Nesneleri
        self.faculty = Faculty.objects.get_or_create()[0]
        self.level = Level.objects.get_or_create(number=1, name="Lisans")[0]
        self.department = Department.objects.create(
            code="SWE",
            faculty=self.faculty
        )

        # 2. HOD Kullanıcısı ve Profili (Zincirleme Bağlantı)
        self.user = SimpleUser.objects.create(
            username="hod_user",
            password="123",
            role="HOD"
        )

        # Head için zorunlu olan Teacher nesnesi
        self.hod_teacher = Teacher.objects.create(
            user=self.user,
            department=self.department
        )

        # Head nesnesi artık teacher'a bağlı
        self.hod = Head.objects.create(
            teacher=self.hod_teacher,
            department=self.department,
            is_active=True
        )

        # 3. Test için başka bir Öğretmen
        self.teacher_user = SimpleUser.objects.create(
            username="teacher_user",
            role="TEACHER"
        )
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            department=self.department
        )

        # 4. Oturum Ayarı
        session = self.client.session
        session["role"] = "HOD"
        session["username"] = "hod_user"
        session.save()

    def test_hod_dashboard_access(self):
        """Dashboard'un ve istatistiklerin yüklendiğini test et."""
        DepartmentStatistic.objects.get_or_create(department=self.department)

        url = reverse('hod:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "SWE")

    def test_unauthorized_access_redirect(self):
        """HOD olmayan kullanıcının yönlendirildiğini test et."""
        self.client.session.flush()
        url = reverse('hod:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_course_detail_view(self):
        """Mevcut bir dersin detay sayfasının açıldığını test et."""
        course = Course.objects.create(
            code="COMP101",
            name="Test Course",
            level=self.level
        )
        dept_course = DepartmentCourse.objects.create(
            department=self.department,
            course=course,
            semester=1
        )

        url = reverse('hod:course_detail', args=[dept_course.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "COMP101")

    def test_teacher_detail_view(self):
        """Öğretmen detay sayfasının açıldığını test et."""
        url = reverse('hod:teacher_detail', args=[self.teacher.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "teacher_user")