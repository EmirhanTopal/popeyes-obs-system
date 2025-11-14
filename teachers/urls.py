from django.urls import path
from . import views

app_name = 'teachers'

urlpatterns = [
    # Ana sayfalar
    path('dashboard/', views.teacher_dashboard, name='dashboard'),
    path('profile/', views.teacher_profile, name='profile'),
    path('contact-info/', views.update_contact_info, name='update_contact_info'),
    
    # Program yönetimi
    path('schedule/', views.manage_schedule, name='manage_schedule'),
    path('office-hours/', views.manage_office_hours, name='manage_office_hours'),
    
    # Ders yönetimi
    path('courses/', views.course_management, name='course_management'),
    path('courses/<int:course_id>/learning-outcomes/', views.manage_learning_outcomes, name='manage_learning_outcomes'),
    path('learning-outcome/<int:outcome_id>/edit/', views.edit_learning_outcome, name='edit_learning_outcome'),
    path('learning-outcome/<int:outcome_id>/delete/', views.delete_learning_outcome, name='delete_learning_outcome'),
    path('courses/<int:course_id>/grades/', views.grade_management, name='grade_management'),
    path('courses/<int:course_id>/attendance/', views.attendance_management, name='attendance_management'),
]