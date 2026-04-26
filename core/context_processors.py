from core.models import StoreSettings
from django.conf import settings

def store_settings(request):
    return {
        "STORE_SETTINGS": StoreSettings.get_solo(),
        "META_PIXEL_ID": getattr(settings, "META_PIXEL_ID", ""),
    }
META_PIXEL_ID = "787936810990680"