from django.contrib import admin
from .models import SimpleUser

@admin.register(SimpleUser)
class SimpleUserAdmin(admin.ModelAdmin):
    list_display = ("username", "role")
    search_fields = ("username",)
    list_filter = ("role",)

