from django.test import TestCase, Client
from django.urls import reverse
from .models import Head, SimpleUser
from departments.models import Department, Faculty, DepartmentStatistic
from teachers.models import Teacher
from courses.models import Course, CourseOffering
from academics.models import Level


class HODViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Altyapı Nesnelerini Güvenli Oluşturma
        try:
            self.faculty = Faculty.objects.get_or_create(name="Engineering")[0]
        except:
            self.faculty = Faculty.objects.get_or_create()[0]

        try:
            self.level = Level.objects.get_or_create(number=1, name="Undergraduate")[0]
        except:
            self.level = Level.objects.get_or_create(number=1)[0]

        self.department = Department.objects.create(
            code="SWE",
            faculty=self.faculty
        )

        # 2. HOD Kullanıcısı ve Profili
        self.user = SimpleUser.objects.create(
            username="hod_user",
            password="123",
            role="HOD"
        )
        self.hod = Head.objects.create(
            head_user=self.user,
            department=self.department,
            is_active=True
        )

        # 3. Öğretmen Nesnesi
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
        self.client.session.flush()  # Oturumu temizle
        url = reverse('hod:dashboard')
        response = self.client.get(url)
        # 302 Redirect (Login sayfasına)
        self.assertEqual(response.status_code, 302)

    def test_course_detail_view(self):
        """Mevcut bir dersin detay sayfasının açıldığını test et."""
        # Test için manuel bir ders oluşturuyoruz (View üzerinden değil)
        course = Course.objects.create(
            code="COMP101",
            name="Test Course",
            level=self.level
        )
        # Bölüm dersi ilişkisi
        from departments.models import DepartmentCourse
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