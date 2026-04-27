from django.db import models
from django.urls import reverse
from django.utils.text import slugify


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
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
        verbose_name="القسم"
    )
    name = models.CharField(max_length=180)
    slug = models.SlugField(max_length=180, unique=True, blank=True, null=True)
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

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.name, allow_unicode=True)
            slug = base_slug or "product"
            counter = 1

            while Product.objects.exclude(pk=self.pk).filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

            self.slug = slug

        super().save(*args, **kwargs)

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
        """
        آمن للنشر: لا يسمح بأي خطأ Storage أن يكسر الموقع.
        """
        try:
            img = self.images.filter(is_primary=True).first() or self.images.first()
            if img and img.image:
                return img.image.url
        except Exception:
            pass
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
        ("STD", "مقاس موحد"),
        ("XS", "XS"),
        ("S", "S"),
        ("M", "M"),
        ("L", "L"),
        ("XL", "XL"),
        ("XXL", "XXL"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")

    size = models.CharField(
        max_length=5,
        choices=SIZE_CHOICES,
        blank=True,
        default="STD",
        verbose_name="المقاس"
    )

    color = models.CharField(max_length=50, verbose_name="اللون")

    color_image = models.ImageField(
        upload_to="variants/%Y/%m/",
        null=True,
        blank=True,
        verbose_name="صورة اللون"
    )

    stock = models.PositiveIntegerField(default=0, verbose_name="المخزون")

    class Meta:
        verbose_name = "متغير"
        verbose_name_plural = "المتغيرات"
        ordering = ["product", "size", "color"]
        constraints = [
            models.UniqueConstraint(fields=["product", "size", "color"], name="uniq_product_variant")
        ]

    def __str__(self):
        size = self.size or "STD"
        return f"{self.product.name} - {size} - {self.color}"

    def save(self, *args, **kwargs):
        if not self.size:
            self.size = "STD"
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.stock > 0