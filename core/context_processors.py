from core.models import StoreSettings

def store_settings(request):
    return {
        "STORE_SETTINGS": StoreSettings.get_solo()
    }