from django import forms
from academics.models import Department, Course
from students.models import Student
from teachers.models import Teacher

class DepartmentForm(forms.ModelForm):
    class Meta:
        model = Department
        fields = ["code", "name"]

class CourseForm(forms.ModelForm):
    class Meta:
        model = Course
        fields = ["code", "name", "department","level"]

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ["full_name","department"]

class StudentForm(forms.ModelForm):
    departments = forms.ModelMultipleChoiceField(
        queryset=Department.objects.all(),
        widget=forms.SelectMultiple(attrs={"size": 6}),
        required=False
    )
    class Meta:
        model = Student
        fields = ["full_name", "student_no", "departments", "advisor","student_level"]
