# dean/urls.py
from django.urls import path
from . import views

app_name = 'dean'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('approvals/courses/', views.course_approvals, name='course_approvals'),
    path('approvals/courses/<int:pk>/approve/', views.approve_course, name='approve_course'),
    path('faculty/settings/', views.faculty_settings, name='faculty_settings'),
]
