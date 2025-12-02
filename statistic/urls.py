# statistic/urls.py
from django.urls import path
from . import views

app_name = 'statistic' # <--- YENİ EKLENDİ

urlpatterns = [
    path('', views.dean_stats, name='dean_stats'),
]