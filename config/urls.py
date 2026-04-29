from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # الموقع الرئيسي
    path("", include("core.urls")),

    # المتجر
    path("", include("store.urls")),

    # الطلبات
    path("", include("orders.urls")),

    # لوحة التحكم المخصصة
    path("admin-panel/", include("dashboard.urls")),

    # لوحة تحكم Django الافتراضية (اختياري)
    path("django-admin/", admin.site.urls),
]

# خدمة ملفات الوسائط (الصور) في وضع DEBUG فقط
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)