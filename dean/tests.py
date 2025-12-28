from django.test import TestCase, Client
from django.urls import reverse
from accounts.models import SimpleUser
from teachers.models import Teacher
from departments.models import Department, Faculty
from .models import Dean

class DeanViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Faculty (Fakülte) Oluşturma
        self.faculty = Faculty.objects.get_or_create()[0]

        # 2. Department (Bölüm) Oluşturma
        # Teacher oluştururken zorunlu olduğu için önce bölümü açıyoruz
        self.dept = Department.objects.get_or_create(
            code="CENG",
            faculty=self.faculty
        )[0]

        # 3. SimpleUser (Hesap) Oluşturma
        self.user = SimpleUser.objects.create(
            username="dekan_user",
            password="123",
            role="DEAN"
        )

        # 4. Teacher (Öğretmen) Oluşturma
        # NOT NULL hatasını önlemek için 'department' ekledik
        # AttributeError hatasını önlemek için 'full_name'i sildik
        self.teacher = Teacher.objects.create(
            user=self.user,
            department=self.dept
        )

        # 5. Dean (Dekan) Profilini Oluşturma
        self.dean = Dean.objects.create(
            teacher=self.teacher,
            faculty=self.faculty
        )

    def set_dean_session(self):
        """View'daki is_dean_logged kontrolü için session ayarı"""
        session = self.client.session
        session['role'] = 'DEAN'
        session['username'] = 'dekan_user'
        session.save()

    def test_dean_dashboard_access(self):
        """Dekan dashboard sayfasının başarılı erişimini test et."""
        self.set_dean_session()
        # Url adının dean:dashboard olduğundan emin ol
        response = self.client.get(reverse('dean:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_redirect(self):
        """Giriş yapmamış dekanın login'e yönlendirildiğini doğrula."""
        response = self.client.get(reverse('dean:dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_student_list_view(self):
        """Öğrenci listeleme fonksiyonunu test et."""
        self.set_dean_session()
        url = reverse('dean:student_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)