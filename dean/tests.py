from django.test import TestCase, Client
from django.urls import reverse
from .models import SimpleUser, Dean
from departments.models import Department, Faculty
from outcomes.models import ProgramOutcome


class DeanViewTest(TestCase):
    def setUp(self):
        self.client = Client()

        # 1. Faculty nesnesi oluşturma
        # HATA BURADAYDI: 'name' yerine senin modelindeki doğru alanı yazmalısın.
        # Eğer alan adını bilmiyorsan sadece Faculty.objects.create() dene
        # veya models.py dosene bakıp 'name' yerine ne yazdığına bak.
        # Tahminim: 'faculty_name' veya sadece boş create.
        try:
            self.faculty = Faculty.objects.create(name="Mühendislik")
        except TypeError:
            # Eğer 'name' yoksa, parametresiz dene veya yaygın isimleri dene
            self.faculty = Faculty.objects.create()

            # 2. SimpleUser oluşturma
        self.user = SimpleUser.objects.create(
            username="dekan_user",
            password="123",
            role="DEAN"
        )

        # 3. Dekan profilini oluşturma
        self.dean = Dean.objects.create(
            user=self.user,
            full_name="Test Dean",
            faculty=self.faculty
        )

        # 4. Bölüm oluşturma (Bölüm modelinde de 'name' yerine başka bir şey olabilir)
        # Hata almamak için şimdilik sadece code veriyoruz
        try:
            self.dept = Department.objects.create(
                code="CENG",
                name="Computer Engineering",
                faculty=self.faculty
            )
        except TypeError:
            self.dept = Department.objects.create(
                code="CENG",
                faculty=self.faculty
            )

    def set_dean_session(self):
        session = self.client.session
        session['role'] = 'DEAN'
        session['username'] = 'dekan_user'
        session.save()

    def test_dean_dashboard_access(self):
        """Dekan dashboard sayfası başarıyla yükleniyor mu?"""
        self.set_dean_session()
        # View fonksiyonuna göre login redirect kontrolü
        response = self.client.get(reverse('dean:dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_unauthorized_redirect(self):
        """Giriş yapmamış birini login'e atıyor mu?"""
        response = self.client.get(reverse('dean:dashboard'))
        self.assertEqual(response.status_code, 302)