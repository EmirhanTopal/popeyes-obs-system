from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import SimpleUser
from .models import Student
from courses.models import Course
from academics.models import Level


class StudentViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Altyapı Nesneleri
        self.level = Level.objects.get_or_create(number=1, name="Lisans")[0]

        # 2. Öğrenci Kullanıcısı
        self.user = SimpleUser.objects.create(
            username="ogrenci_test",
            password="123",
            role="STUDENT"
        )

        # 3. Student Profili
        self.student = Student.objects.create(
            user=self.user,
            student_no="20250001"
        )

    def set_role_session(self, username, role):
        """Oturumu simüle eder"""
        session = self.client.session
        session['username'] = username
        session['role'] = role
        session.save()

    def test_student_dashboard_access(self):
        """Dashboard'un başarıyla açıldığını doğrular."""
        self.set_role_session("ogrenci_test", "STUDENT")
        url = reverse('students:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_student_courses_view(self):
        """Ders listesi sayfasının açıldığını doğrular."""
        self.set_role_session("ogrenci_test", "STUDENT")
        # Ders nesnesi oluşturma (Zorunlu alanlar dahil)
        Course.objects.create(code="SENG101", level=self.level)

        url = reverse('students:courses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_profile_page_loads(self):
        """Profil sayfasının açıldığını doğrular."""
        self.set_role_session("ogrenci_test", "STUDENT")
        url = reverse('students:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access_to_dashboard(self):
        """Giriş yapmamış kullanıcının yönlendirildiğini doğrular."""
        url = reverse('students:dashboard')
        response = self.client.get(url)
        # @require_role dekoratörü genellikle login sayfasına yönlendirir (302)
        self.assertEqual(response.status_code, 302)