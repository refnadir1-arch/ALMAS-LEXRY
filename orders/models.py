from django.conf import settings
from django.db import models

from orders.constants import ORDER_STATUSES, DELIVERY_TYPES


class Order(models.Model):
    code = models.CharField(max_length=20, unique=True)

    # نخليهم كما هم للتوافق (يعبرون عن "أول منتج" في الطلب)
    product = models.ForeignKey("store.Product", on_delete=models.PROTECT, related_name="orders")
    variant = models.ForeignKey("store.Variant", on_delete=models.PROTECT, related_name="orders")

    full_name = models.CharField(max_length=140)
    phone = models.CharField(max_length=30)
    wilaya_code = models.CharField(max_length=2)
    wilaya_name_ar = models.CharField(max_length=80)
    commune_name_ar = models.CharField(max_length=120)

    qty = models.PositiveIntegerField(default=1)  # للتوافق (أول عنصر)
    delivery_type = models.CharField(max_length=10, choices=DELIVERY_TYPES)

    unit_price_dzd = models.PositiveIntegerField()  # للتوافق (أول عنصر)
    shipping_fee_dzd = models.PositiveIntegerField(default=0)
    total_dzd = models.PositiveIntegerField(default=0)

    status = models.CharField(max_length=30, choices=ORDER_STATUSES, default="NEW")
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

    @property
    def items_subtotal_dzd(self) -> int:
        """
        مجموع المنتجات بدون التوصيل.
        إذا كان عندنا OrderItem نستخدمها، وإلا نرجع للحقل القديم (منتج واحد).
        """
        if hasattr(self, "items") and self.items.exists():
            return sum((it.unit_price_dzd * it.qty) for it in self.items.all())
        return int(self.unit_price_dzd or 0) * int(self.qty or 0)

    @property
    def items_count(self) -> int:
        """عدد السطور (OrderItem)"""
        if hasattr(self, "items") and self.items.exists():
            return self.items.count()
        return 1

    @property
    def total_qty(self) -> int:
        """مجموع الكميات لكل المنتجات"""
        if hasattr(self, "items") and self.items.exists():
            return sum(int(it.qty or 0) for it in self.items.all())
        return int(self.qty or 0)

    @property
    def computed_total_dzd(self) -> int:
        """الإجمالي المتوقع = subtotal + shipping"""
        return int(self.items_subtotal_dzd) + int(self.shipping_fee_dzd or 0)


class OrderItem(models.Model):
    """
    سطر داخل الطلب (منتج/متغير/كمية).
    هذا هو الأساس لدعم عدة منتجات في طلب واحد.
    """
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items", verbose_name="الطلب")

    product = models.ForeignKey("store.Product", on_delete=models.PROTECT, related_name="order_items", verbose_name="المنتج")
    variant = models.ForeignKey("store.Variant", on_delete=models.PROTECT, related_name="order_items", verbose_name="المتغير")

    qty = models.PositiveIntegerField(default=1, verbose_name="الكمية")
    unit_price_dzd = models.PositiveIntegerField(verbose_name="سعر الوحدة")

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "عنصر طلب"
        verbose_name_plural = "عناصر الطلب"
        ordering = ["id"]

    def __str__(self):
        return f"{self.order.code} - {self.product} - {self.variant} x{self.qty}"

    @property
    def line_total_dzd(self) -> int:
        return int(self.unit_price_dzd or 0) * int(self.qty or 0)


class OrderStatusHistory(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="history")
    status = models.CharField(max_length=30, choices=ORDER_STATUSES)
    note = models.CharField(max_length=255, blank=True)
    changed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    changed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "سجل حالة الطلب"
        verbose_name_plural = "سجل حالات الطلب"
        ordering = ["changed_at"]

    def __str__(self):
        return f"{self.order.code} - {self.status}"