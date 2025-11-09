from django.urls import path
from . import views

app_name = 'hod'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
]
