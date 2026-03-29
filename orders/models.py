from django.conf import settings
from django.db import models
from orders.constants import ORDER_STATUSES, DELIVERY_TYPES

class Order(models.Model):
    code = models.CharField(max_length=20, unique=True)

    product = models.ForeignKey("store.Product", on_delete=models.PROTECT, related_name="orders")
    variant = models.ForeignKey("store.Variant", on_delete=models.PROTECT, related_name="orders")

    full_name = models.CharField(max_length=140)
    phone = models.CharField(max_length=30)
    wilaya_code = models.CharField(max_length=2)
    wilaya_name_ar = models.CharField(max_length=80)
    commune_name_ar = models.CharField(max_length=120)

    qty = models.PositiveIntegerField(default=1)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPES)

    unit_price_dzd = models.PositiveIntegerField()
    shipping_fee_dzd = models.PositiveIntegerField(default=0)
    total_dzd = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=20, choices=ORDER_STATUSES, default="NEW")
    customer_note = models.TextField(blank=True)
    admin_note = models.TextField(blank=True)

    shipped_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "طلب"
        verbose_name_plural = "الطلبات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.code

class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=20, choices=ORDER_STATUSES)
    note = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل حالة الطلب"
        verbose_name_plural = "سجل حالات الطلب"
        ordering = ["changed_at"]

    def __str__(self):
        return f"{self.order.code} - {self.status}"