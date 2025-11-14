from django.urls import path
from . import views

app_name = 'hod'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path("delete-course/<int:pk>/", views.delete_course, name="delete_course"),
    path("teacher/<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("course/create/", views.create_course, name="create_course"),


]
