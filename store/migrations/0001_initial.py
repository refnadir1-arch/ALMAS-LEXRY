from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name="Category",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=100)),
                ("slug", models.SlugField(max_length=120, unique=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Product",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=180)),
                ("slug", models.SlugField(max_length=180, unique=True)),
                ("description", models.TextField(blank=True)),
                ("price_dzd", models.PositiveIntegerField()),
                ("discount_percent", models.PositiveIntegerField(default=0)),
                ("is_active", models.BooleanField(default=True)),
                ("sales_count", models.PositiveIntegerField(default=0)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("category", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="products", to="store.category")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="ProductImage",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("image", models.ImageField(upload_to="products/%Y/%m/")),
                ("is_primary", models.BooleanField(default=False)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="images", to="store.product")),
            ],
        ),
        migrations.CreateModel(
            name="Variant",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("size", models.CharField(choices=[("XS","XS"),("S","S"),("M","M"),("L","L"),("XL","XL"),("XXL","XXL")], max_length=5)),
                ("color", models.CharField(max_length=50)),
                ("stock", models.PositiveIntegerField(default=0)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="variants", to="store.product")),
            ],
            options={"ordering": ["product", "size", "color"]},
        ),
        migrations.AddConstraint(
            model_name="variant",
            constraint=models.UniqueConstraint(fields=("product", "size", "color"), name="uniq_product_variant"),
        ),
    ]