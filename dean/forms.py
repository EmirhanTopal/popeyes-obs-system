from django import forms
from departments.models import Department
from courses.models import Course
from teachers.models import Teacher
from students.models import Student
from faculty.models import Faculty


# ===========================
#  Bölüm Ekleme Formu
# ===========================
class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["code", "name", "faculty"]

    # Dean panelinden faculty seçilmesin → view içinde otomatik atanacak
    faculty = forms.ModelChoiceField(
        queryset=Faculty.objects.all(),
        required=False,
        widget=forms.HiddenInput()
    )


# ===========================
#  Ders Ekleme Formu
# ===========================
class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "credit", "ects", "level", "course_type"]

    # Bölüm eklenmiyor çünkü head oluşturuyor — Dean sadece admin olarak ders ekleyebilir.


# ===========================
#  Öğretmen Ekleme Formu
# ===========================
class TeacherForm(forms.ModelForm):
    # Bunlar MODEL alanı DEĞİL → ekstra form alanları
    first_name = forms.CharField(label="Ad", max_length=50)
    last_name = forms.CharField(label="Soyad", max_length=50)
    email = forms.EmailField(label="E-posta")

    class Meta:
        model = Teacher
        fields = [
            "employee_id",
            "department",
            "teacher_type",
            "academic_title",
            "expertise_area",
            "office_location",
            "office_phone",
            "personal_website",
            "linkedin",
            "google_scholar",
            "researchgate",
            "orcid",
        ]

    def save(self, commit=True):
        # User oluştur
        from django.contrib.auth import get_user_model
        User = get_user_model()

        user = User.objects.create_user(
            username=self.cleaned_data["email"],
            email=self.cleaned_data["email"],
            first_name=self.cleaned_data["first_name"],
            last_name=self.cleaned_data["last_name"],
            password="123456"  # otomatik şifre
        )

        # Teacher oluştur (ModelForm)
        teacher = super().save(commit=False)
        teacher.user = user

        if commit:
            teacher.save()

        return teacher