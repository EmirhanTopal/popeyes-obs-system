from django.urls import path
from . import views

app_name = "hod"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("course/create/", views.create_course, name="create_course"),
    path("course/<int:course_id>/", views.course_detail, name="course_detail"),
    path("course/<int:pk>/edit/", views.course_edit, name="course_edit"),
    path("delete-course/<int:pk>/", views.delete_course, name="delete_course"),
    path("teacher/<int:pk>/", views.teacher_detail, name="teacher_detail"),
    path("course/<int:course_id>/add-offering/", views.add_offering, name="add_offering"),
    path("course/add-existing/", views.add_existing_course, name="add_existing_course"),

]
