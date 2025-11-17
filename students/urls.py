# students/urls.py
from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile, name='profile'),
    path('courses/', views.courses, name='courses'),
    path('attendance/', views.attendance, name='attendance'),
    path('', views.dashboard_redirect, name='root'),

    
    path('admin/profile/<str:student_id>/', views.admin_student_profile, name='admin_profile'),
]