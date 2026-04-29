from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("", include("core.urls")),
    path("", include("store.urls")),
    path("", include("orders.urls")),
    path("admin-panel/", include("dashboard.urls")),
    path("django-admin/", admin.site.urls),
]

# ✅ نخدم media دائماً (حتى في الإنتاج)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)