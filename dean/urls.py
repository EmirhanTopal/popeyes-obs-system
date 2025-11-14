# dean/urls.py
from django.urls import path
from . import views

app_name = 'dean'

urlpatterns = [
    path("pending-courses/", views.pending_courses, name="pending_courses"),
    path("approve/<int:pk>/", views.approve_course, name="approve_course"),
    path("reject/<int:pk>/", views.reject_course, name="reject_course"),
]
