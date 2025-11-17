from django.urls import path
from . import views

app_name = 'outcomes'

urlpatterns = [
    path('dekan-dashboard/', views.dekan_dashboard, name='dekan_dashboard'),
]