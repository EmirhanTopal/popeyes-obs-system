from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import SimpleUser
from .models import Student
from courses.models import Course, CourseOffering, Enrollment
from academics.models import Level


class StudentViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Altyapı Nesneleri (Level zorunluluğu)
        self.level = Level.objects.get_or_create(number=1, name="Lisans")[0]

        # 2. Öğrenci Kullanıcısı (SimpleUser)
        # Student modelindeki email @property olduğu için email bilgisini buraya yazıyoruz
        self.user = SimpleUser.objects.create(
            username="ogrenci_test",
            password="123",
            email="ogrenci@test.com",
            role="STUDENT"
        )

        # 3. Student Profili
        # HATA ALAN 'email' parametresini sildik, çünkü modelde @property olarak tanımlı
        self.student = Student.objects.create(
            user=self.user,
            student_no="20250001"
        )

    def set_role_session(self, username, role):
        """Oturumu (session) simüle eder"""
        session = self.client.session
        session['username'] = username
        session['role'] = role
        session.save()

    def test_student_dashboard_access(self):
        """Dashboard'un başarıyla açıldığını ve öğrencinin bulunduğunu doğrular."""
        self.set_role_session("ogrenci_test", "STUDENT")
        url = reverse('students:dashboard')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['student'], self.student)

    def test_student_courses_view(self):
        """Ders listesi sayfasının açıldığını ve kayıtların çekildiğini doğrular."""
        self.set_role_session("ogrenci_test", "STUDENT")

        # Test verisi: Ders -> Şube (Offering) -> Kayıt (Enrollment)
        course = Course.objects.create(code="SENG101", name="Software Eng", level=self.level)
        offering = CourseOffering.objects.create(course=course, year=2025, semester=1)
        # Enrollment modelinde related_name='enrollments' olduğunu varsayıyoruz
        Enrollment.objects.create(student=self.student, offering=offering)

        url = reverse('students:courses')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['enrollments'].exists())

    def test_profile_page_loads(self):
        """Profil sayfasının başarıyla yüklendiğini kontrol eder."""
        self.set_role_session("ogrenci_test", "STUDENT")
        url = reverse('students:profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_attendance_page_loads(self):
        """Devamsızlık sayfasının başarıyla yüklendiğini kontrol eder."""
        self.set_role_session("ogrenci_test", "STUDENT")
        url = reverse('students:attendance')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_access_to_dashboard(self):
        """Oturum açmamış kullanıcının dashboard'dan yönlendirildiğini doğrular."""
        url = reverse('students:dashboard')
        response = self.client.get(url)
        # @require_role dekoratörü yetkisiz girişte 302 yönlendirmesi yapar
        self.assertEqual(response.status_code, 302)