# academics/urls.py
from django.urls import path
from . import views

app_name = 'academics'

urlpatterns = [
    path('faculties/', views.faculty_list, name='faculty_list'),
    path('departments/', views.department_list, name='department_list'),
    path('courses/', views.course_list, name='course_list'),
    path('courses/<int:pk>/', views.course_detail, name='course_detail'),
]
