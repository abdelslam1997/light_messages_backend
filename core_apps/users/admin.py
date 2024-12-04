from django.contrib import admin
from .models import LightMessagesUser


class LightMessagesUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "is_active", "is_staff", "is_superuser", "profile_image")
    search_fields = ("email", "id")
    list_filter = ("is_active", "is_staff", "is_superuser")
    ordering = ("id",)
    readonly_fields = ("id", "date_joined", "last_login")



admin.site.register(LightMessagesUser, LightMessagesUserAdmin)