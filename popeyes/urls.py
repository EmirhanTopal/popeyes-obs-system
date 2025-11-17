from django.contrib import admin
from django.urls import path, include
from accounts.views import login_view, logout_view

urlpatterns = [
    path("admin/", admin.site.urls),

    path('', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path("accounts/login/", login_view),
    path('students/', include('students.urls')),
    path('teachers/', include('teachers.urls')),
    path('hod/', include('hod.urls')),
    path('dean/', include('dean.urls')),
    path('academics/', include('academics.urls')),  
    path('admin/outcomes/', include('outcomes.urls')),
]
