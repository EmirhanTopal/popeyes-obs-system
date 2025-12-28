from django.urls import path
from . import views
from outcomes.views import program_outcome_list

app_name = "dean"

urlpatterns = [
    # 🎯 Sadece dashboard kalsın
    path("", views.dekan_dashboard, name="dashboard"),
    path("students/", views.student_list, name="student_list"),
    path("students/<int:student_id>/program-outcomes/", views.student_po_report, name="student_po_report"),
    path("program-outcomes/", program_outcome_list, name="program_outcome_list")
]
