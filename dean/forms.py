# dean/forms.py
from django import forms
from departments.models import Department
from courses.models import Course
from teachers.models import Teacher
from students.models import Student


class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["code", "name", "faculty"]
        labels = {"code": "Bölüm Kodu", "name": "Bölüm Adı", "faculty": "Fakülte"}
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "faculty": forms.Select(attrs={"class": "form-select"}),
        }


class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "credit", "department"]
        labels = {"code": "Ders Kodu", "name": "Ders Adı", "credit": "Kredi", "department": "Bölüm"}
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "credit": forms.NumberInput(attrs={"class": "form-control"}),
            "department": forms.SelectMultiple(attrs={"class": "form-select", "size": "4"}),
        }


"""class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["name", "e_mail", "department"]
        labels = {"name": "Ad Soyad", "e_mail": "E-posta", "department": "Bölüm"}
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "e_mail": forms.EmailInput(attrs={"class": "form-control"}),
            "department": forms.Select(attrs={"class": "form-select"}),
        }"""


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_no", "full_name", "departments"]
        labels = {"student_no": "Öğrenci No", "full_name": "Ad Soyad", "departments": "Bölüm(ler)"}
        widgets = {
            "student_no": forms.TextInput(attrs={"class": "form-control"}),
            "full_name": forms.TextInput(attrs={"class": "form-control"}),
            "departments": forms.SelectMultiple(attrs={"class": "form-select", "size": "4"}),
        }
