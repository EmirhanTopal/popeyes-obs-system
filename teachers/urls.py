from django.urls import path
from . import views
from courses.models import Course

app_name = 'teachers'

urlpatterns = [
    # Ana sayfalar
    path('', views.teacher_dashboard, name='index'),
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('profile/', views.teacher_profile, name='profile'),
    path('contact-info/', views.update_contact_info, name='update_contact_info'),

    # Program yönetimi
    path('schedule/', views.manage_schedule, name='manage_schedule'),
    path("schedule/<int:pk>/edit/", views.edit_schedule, name="edit_schedule"),
    path("schedule/<int:pk>/delete/", views.delete_schedule, name="delete_schedule"),
    path('office-hours/', views.manage_office_hours, name='manage_office_hours'),
    path("office_hours/edit/<int:id>/", views.edit_office_hour, name="edit_office_hour"),
    path("office_hours/delete/<int:id>/", views.delete_office_hour, name="delete_office_hour"),

    # Ders yönetimi
    path('courses/', views.course_management, name='course_management'),
    path('courses/<int:offering_id>/attendance/', views.attendance_management, name='attendance_management'),
    path('courses/<int:offering_id>/components/', views.manage_components, name='manage_components'),
    path("courses/<int:offering_id>/learning-outcomes/", views.manage_learning_outcomes, name="manage_learning_outcomes"),
    path('courses/<int:offering_id>/grades/', views.manage_grades, name='manage_grades'),



]