from django.apps import AppConfig


class MessengerConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core_apps.messenger"

    def ready(self):
        from . import signals  # Ensure signals are imported
