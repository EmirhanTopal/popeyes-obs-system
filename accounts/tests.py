from django.test import TestCase, Client
from django.urls import reverse
from .models import SimpleUser


class LoginViewTest(TestCase):
    def setUp(self):
        # Testler için örnek kullanıcılar oluşturuyoruz
        self.client = Client()
        self.student = SimpleUser.objects.create(
            username="ogrenci1",
            password="123",
            role="STUDENT"
        )
        self.teacher = SimpleUser.objects.create(
            username="ogretmen1",
            password="123",
            role="TEACHER"
        )
        # Url adın urls.py'da farklıysa burayı düzenleyebilirsin
        try:
            self.login_url = reverse('login')
            self.logout_url = reverse('logout')
        except:
            self.login_url = "/login/"  # Fallback: manuel path
            self.logout_url = "/logout/"

    def test_login_page_loads(self):
        """Giriş sayfası başarıyla yükleniyor mu?"""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "auth/login.html")

    def test_successful_student_login(self):
        """Öğrenci girişi başarılı mı ve doğru yere yönlendiriyor mu?"""
        data = {'username': 'ogrenci1', 'password': '123'}
        response = self.client.post(self.login_url, data)

        # fetch_redirect_response=False: Hedef sayfanın (200 OK) verip vermediğine bakma,
        # sadece yönlendirmenin doğru adrese yapıldığını onayla.
        self.assertRedirects(response, "/students/", fetch_redirect_response=False)
        self.assertEqual(self.client.session['role'], 'STUDENT')

    def test_successful_teacher_login(self):
        """Öğretmen girişi başarılı mı ve doğru yere yönlendiriyor mu?"""
        data = {'username': 'ogretmen1', 'password': '123'}
        response = self.client.post(self.login_url, data)

        self.assertRedirects(response, "/teachers/", fetch_redirect_response=False)
        self.assertEqual(self.client.session['role'], 'TEACHER')

    def test_invalid_login(self):
        """Hatalı şifre ile giriş denemesi başarısız oluyor mu?"""
        data = {'username': 'ogrenci1', 'password': 'yanlis_sifre'}
        response = self.client.post(self.login_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kullanıcı adı veya şifre hatalı.")
        self.assertNotIn('role', self.client.session)

    def test_already_logged_in_redirect(self):
        """Zaten giriş yapmış bir kullanıcı login sayfasına giderse yönlendiriliyor mu?"""
        session = self.client.session
        session['role'] = 'STUDENT'
        session.save()

        response = self.client.get(self.login_url)
        self.assertRedirects(response, "/students/", fetch_redirect_response=False)

    def test_logout(self):
        """Çıkış işlemi session'ı temizliyor mu?"""
        session = self.client.session
        session['role'] = 'STUDENT'
        session.save()

        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url, fetch_redirect_response=False)
        self.assertEqual(len(self.client.session.keys()), 0)