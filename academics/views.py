# academics/views.py
from django.shortcuts import render, get_object_or_404
from .models import Faculty, Department, Level, Course


def faculty_list(request):
    faculties = Faculty.objects.all()
    return render(request, 'academics/faculty_list.html', {'faculties': faculties})


def department_list(request):
    departments = Department.objects.select_related('faculty').all()
    return render(request, 'academics/department_list.html', {'departments': departments})


def course_list(request):
    courses = Course.objects.select_related('level').prefetch_related('department').all()
    return render(request, 'academics/course_list.html', {'courses': courses})


def course_detail(request, pk):
    course = get_object_or_404(Course, pk=pk)
    return render(request, 'academics/course_detail.html', {'course': course})
