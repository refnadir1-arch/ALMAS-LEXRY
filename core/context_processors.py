from __future__ import annotations

from core.models import StoreSettings


def store_settings(request):
    """
    Context processor آمن: لا يسمح لأي خطأ في StoreSettings أن يكسر كل الموقع.
    """
    settings_obj = None
    meta_pixel_id = ""

    try:
        # إذا عندك get_solo
        if hasattr(StoreSettings, "get_solo"):
            settings_obj = StoreSettings.get_solo()
        else:
            settings_obj = StoreSettings.objects.first()
    except Exception:
        settings_obj = StoreSettings()

    try:
        meta_pixel_id = getattr(settings_obj, "meta_pixel_id", "") or getattr(settings_obj, "META_PIXEL_ID", "") or ""
    except Exception:
        meta_pixel_id = ""

    return {
        "STORE_SETTINGS": settings_obj,
        "META_PIXEL_ID": meta_pixel_id,
    }