from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "قسم"
        verbose_name_plural = "الأقسام"
        ordering = ["name"]

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True)
    description = models.TextField(blank=True)

    price_dzd = models.PositiveIntegerField(verbose_name="السعر")
    compare_at_price_dzd = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="السعر قبل التخفيض"
    )
    cost_price_dzd = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="سعر التكلفة"
    )

    video_url = models.URLField(blank=True, default="", verbose_name="رابط الفيديو")
    sku = models.CharField(max_length=120, blank=True, default="", verbose_name="SKU")

    seo_title = models.CharField(max_length=180, blank=True, default="", verbose_name="عنوان SEO")
    seo_description = models.TextField(blank=True, default="", verbose_name="وصف SEO")

    is_active = models.BooleanField(default=True)

    sales_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "منتج"
        verbose_name_plural = "المنتجات"
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    @property
    def discount_percent(self):
        if self.compare_at_price_dzd and self.compare_at_price_dzd > self.price_dzd:
            return int(round((self.compare_at_price_dzd - self.price_dzd) * 100 / self.compare_at_price_dzd))
        return 0

    @property
    def final_price_dzd(self):
        return self.price_dzd

    @property
    def has_discount(self):
        return bool(self.compare_at_price_dzd and self.compare_at_price_dzd > self.price_dzd)

    @property
    def primary_image(self):
        img = self.images.filter(is_primary=True).first() or self.images.first()
        if img and img.image:
            return img.image.url
        return ""

    def get_absolute_url(self):
        return reverse("product_detail", kwargs={"slug": self.slug})

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/%Y/%m/")
    is_primary = models.BooleanField(default=False)

    class Meta:
        verbose_name = "صورة منتج"
        verbose_name_plural = "صور المنتجات"

    def __str__(self):
        return f"صورة - {self.product.name}"

class Variant(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=5, choices=SIZE_CHOICES)
    color = models.CharField(max_length=50)
    stock = models.PositiveIntegerField(default=0)

    class Meta:
        verbose_name = "متغير"
        verbose_name_plural = "المتغيرات"
        ordering = ["product", "size", "color"]
        constraints = [
            models.UniqueConstraint(fields=["product", "size", "color"], name="uniq_product_variant")
        ]

    def __str__(self):
        return f"{self.product.name} - {self.size} - {self.color}"

    @property
    def is_available(self):
        return self.stock > 0