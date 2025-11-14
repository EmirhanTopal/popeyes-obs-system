from django.urls import path
from . import views

app_name = "dean"

urlpatterns = [
    path("", views.dashboard, name="dashboard"),

    # Yeni ders onayı (Course)
    path("course/approve/<int:pk>/", views.approve_course, name="approve_course"),
    path("course/reject/<int:pk>/", views.reject_course, name="reject_course"),

    # Bölüme ders ekleme onayı (DepartmentCourse)
    path("department-course/approve/<int:pk>/", views.approve_department_course, name="approve_department_course"),
    path("department-course/reject/<int:pk>/", views.reject_department_course, name="reject_department_course"),
]
