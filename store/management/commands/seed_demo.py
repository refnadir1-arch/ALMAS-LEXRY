from io import BytesIO
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.db import transaction
from PIL import Image, ImageDraw

from core.models import StoreSettings, Review
from store.models import Category, Product, Variant, ProductImage


class Command(BaseCommand):
    help = "إنشاء بيانات تجريبية للمتجر ولوحة التحكم"

    @transaction.atomic
    def handle(self, *args, **kwargs):
        admin_group, _ = Group.objects.get_or_create(name="Admin")
        staff_group, _ = Group.objects.get_or_create(name="Staff")

        if not User.objects.filter(username="admin").exists():
            user = User.objects.create_superuser("admin", "", "admin12345")
            user.groups.add(admin_group)

        if not User.objects.filter(username="staff").exists():
            user = User.objects.create_user("staff", password="staff12345", is_staff=True)
            user.groups.add(staff_group)

        settings_obj = StoreSettings.get_solo()
        settings_obj.store_name = "ALMAS LUXRY"
        settings_obj.phone = "0774474746"
        settings_obj.whatsapp = "0774474746"
        settings_obj.address = "الجزائر"
        settings_obj.shipping_home_fee_dzd = 800
        settings_obj.shipping_office_fee_dzd = 500
        settings_obj.hero_title = "أناقتك تبدأ من هنا"
        settings_obj.hero_subtitle = "اختيارات نسائية فاخرة بلمسة راقية — الدفع عند الاستلام فقط."
        settings_obj.save()

        categories_data = [
            ("فساتين", "dresses"),
            ("أطقم", "sets"),
            ("عبايات", "abayas"),
            ("جديد", "new"),
        ]

        category_objs = []
        for name, slug in categories_data:
            category, _ = Category.objects.get_or_create(
                slug=slug,
                defaults={"name": name, "is_active": True}
            )
            category_objs.append(category)

        dresses = category_objs[0]
        sets = category_objs[1]
        abayas = category_objs[2]
        new_cat = category_objs[3]

        products_data = [
            {
                "name": "فستان مخملي أسود فاخر",
                "slug": "dress-black-velvet-lux",
                "category": dresses,
                "price": 14500,
                "compare": 17500,
                "description": "فستان أنيق بتصميم فاخر يناسب السهرات والمناسبات الخاصة."
            },
            {
                "name": "فستان سهرة أخضر أنيق",
                "slug": "dress-green-evening-elegant",
                "category": dresses,
                "price": 16900,
                "compare": 19900,
                "description": "فستان سهرة بتفاصيل أنثوية راقية ولمسة عصرية جذابة."
            },
            {
                "name": "فستان أزرق ناعم",
                "slug": "dress-blue-soft",
                "category": dresses,
                "price": 15900,
                "compare": 18900,
                "description": "فستان طويل بإطلالة ناعمة ومريحة، مثالي للمناسبات."
            },
            {
                "name": "فستان خمري فاخر",
                "slug": "dress-burgundy-lux",
                "category": new_cat,
                "price": 14900,
                "compare": 17900,
                "description": "فستان راقٍ بلمسة فخامة واضحة وأناقة أنثوية جذابة."
            },
            {
                "name": "طقم أنثوي عصري",
                "slug": "set-modern-feminine",
                "category": sets,
                "price": 12900,
                "compare": 14900,
                "description": "طقم عصري مناسب للإطلالات اليومية الأنيقة."
            },
            {
                "name": "عباية سوداء راقية",
                "slug": "abaya-black-premium",
                "category": abayas,
                "price": 11800,
                "compare": 13200,
                "description": "عباية بتفاصيل راقية تمنحك حضورًا أنيقًا ومميزًا."
            },
            {
                "name": "فستان سهرة أنيق",
                "slug": "dress-evening-elegant",
                "category": dresses,
                "price": 16900,
                "compare": None,
                "description": "تصميم أنيق مناسب للسهرات والمناسبات الراقية."
            },
        ]

        for idx, item in enumerate(products_data, start=1):
            product, created = Product.objects.get_or_create(
                slug=item["slug"],
                defaults={
                    "category": item["category"],
                    "name": item["name"],
                    "description": item["description"],
                    "price_dzd": item["price"],
                    "compare_at_price_dzd": item["compare"],
                    "cost_price_dzd": int(item["price"] * 0.65),
                    "video_url": "",
                    "sku": f"SKU-{idx:03d}",
                    "seo_title": item["name"],
                    "seo_description": f"{item['name']} من ALMAS LUXRY",
                    "is_active": True,
                }
            )

            if created:
                Variant.objects.create(product=product, size="S", color="أسود", stock=3)
                Variant.objects.create(product=product, size="M", color="خمري", stock=4)
                Variant.objects.create(product=product, size="L", color="أخضر", stock=2)
                Variant.objects.create(product=product, size="XL", color="أزرق", stock=0)

                img = self.make_placeholder_image(product.name)
                ProductImage.objects.create(
                    product=product,
                    image=ContentFile(img, name=f"{item['slug']}.jpg"),
                    is_primary=True
                )

        if Review.objects.count() == 0:
            Review.objects.create(name="سارة", stars=5, text="خدمة راقية وتعامل محترم جدًا، والمنتج جميل كما في الصور.")
            Review.objects.create(name="أمينة", stars=5, text="التوصيل سريع جدًا والتغليف أنيق، شكراً لكم.")
            Review.objects.create(name="ليلى", stars=4, text="الخامة ممتازة والمقاس مناسب، تجربة موفقة.")
            Review.objects.create(name="سمية", stars=5, text="تعامل احترافي ومنتج أنيق جدًا.")

        self.stdout.write(self.style.SUCCESS("تم إنشاء البيانات التجريبية بنجاح."))
        self.stdout.write(self.style.SUCCESS("admin / admin12345"))
        self.stdout.write(self.style.SUCCESS("staff / staff12345"))

    def make_placeholder_image(self, title):
        image = Image.new("RGB", (1200, 1400), (20, 20, 20))
        draw = ImageDraw.Draw(image)
        draw.rectangle((60, 60, 1140, 1340), outline=(194, 24, 91), width=5)
        draw.text((120, 120), "ALMAS LUXRY", fill=(212, 180, 120))
        draw.text((120, 220), title, fill=(255, 255, 255))
        bio = BytesIO()
        image.save(bio, format="JPEG", quality=90)
        return bio.getvalue()