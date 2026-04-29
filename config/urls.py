from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from orders.views import create_admin_once

urlpatterns = [
    path("", include("core.urls")),
    path("", include("store.urls")),
    path("", include("orders.urls")),

    path("admin-panel/", include("dashboard.urls")),
    path("django-admin/", admin.site.urls),

    # ✅ مؤقت لإنشاء الأدمن
    path("create-admin-once/", create_admin_once),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)