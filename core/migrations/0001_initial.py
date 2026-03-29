from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="StoreSettings",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("store_name", models.CharField(default="ALMAS LUXRY", max_length=120)),
                ("phone", models.CharField(default="0774474746", max_length=30)),
                ("whatsapp", models.CharField(default="0774474746", max_length=30)),
                ("address", models.CharField(default="الجزائر", max_length=255)),
                ("shipping_home_fee_dzd", models.PositiveIntegerField(default=800)),
                ("shipping_office_fee_dzd", models.PositiveIntegerField(default=500)),
                ("hero_title", models.CharField(default="أناقتك تبدأ من هنا", max_length=180)),
                ("hero_subtitle", models.CharField(default="اختيارات نسائية فاخرة بلمسة راقية — الدفع عند الاستلام فقط.", max_length=255)),
                ("instagram_url", models.URLField(blank=True, default="")),
                ("facebook_url", models.URLField(blank=True, default="")),
                ("tiktok_url", models.URLField(blank=True, default="")),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="Review",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120)),
                ("stars", models.PositiveSmallIntegerField(default=5)),
                ("text", models.TextField()),
                ("is_active", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={"ordering": ["-created_at"]},
        ),
    ]