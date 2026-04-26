from django.apps import AppConfig
from django.contrib.auth import get_user_model

class DashboardConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "dashboard"

    def ready(self):
        User = get_user_model()
        if not User.objects.filter(username="superadmin").exists():
            User.objects.create_superuser(
                username="superadmin",
                email="admin@example.com",
                password="Admin12345"
            )