from django.db import models

class StoreSettings(models.Model):
    store_name = models.CharField(max_length=120, default="ALMAS LUXRY")
    phone = models.CharField(max_length=30, default="0774474746")
    whatsapp = models.CharField(max_length=30, default="0774474746")
    address = models.CharField(max_length=255, default="الجزائر")

    shipping_home_fee_dzd = models.PositiveIntegerField(default=800)
    shipping_office_fee_dzd = models.PositiveIntegerField(default=500)

    hero_title = models.CharField(max_length=180, default="أناقتك تبدأ من هنا")
    hero_subtitle = models.CharField(
        max_length=255,
        default="اختيارات نسائية فاخرة بلمسة راقية — الدفع عند الاستلام فقط."
    )

    instagram_url = models.URLField(blank=True, default="")
    facebook_url = models.URLField(blank=True, default="")
    tiktok_url = models.URLField(blank=True, default="")

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "إعدادات المتجر"
        verbose_name_plural = "إعدادات المتجر"

    def __str__(self):
        return self.store_name

    @classmethod
    def get_solo(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

class Review(models.Model):
    name = models.CharField(max_length=120)
    stars = models.PositiveSmallIntegerField(default=5)
    text = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "رأي زبونة"
        verbose_name_plural = "آراء الزبونات"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name} - {self.stars}/5"