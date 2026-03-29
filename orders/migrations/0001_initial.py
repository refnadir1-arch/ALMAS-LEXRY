from django.db import migrations, models
import django.db.models.deletion
from django.conf import settings

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("store", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="Order",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("code", models.CharField(max_length=20, unique=True)),
                ("full_name", models.CharField(max_length=140)),
                ("phone", models.CharField(max_length=30)),
                ("wilaya_code", models.CharField(max_length=2)),
                ("wilaya_name_ar", models.CharField(max_length=80)),
                ("commune_name_ar", models.CharField(max_length=120)),
                ("qty", models.PositiveIntegerField(default=1)),
                ("delivery_type", models.CharField(choices=[("HOME","إلى باب المنزل"),("OFFICE","إلى مكتب التوصيل")], max_length=10)),
                ("unit_price_dzd", models.PositiveIntegerField()),
                ("shipping_fee_dzd", models.PositiveIntegerField(default=0)),
                ("total_dzd", models.PositiveIntegerField(default=0)),
                ("status", models.CharField(choices=[("NEW","جديد"),("CONTACTED","تم التواصل"),("CONFIRMED","مؤكد"),("PREPARING","قيد التحضير"),("SHIPPED","تم الشحن"),("OUT_FOR_DELIVERY","قيد التوصيل"),("DELIVERED","تم التسليم"),("CANCELED","ملغي")], default="NEW", max_length=20)),
                ("customer_note", models.TextField(blank=True)),
                ("admin_note", models.TextField(blank=True)),
                ("shipped_at", models.DateTimeField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("product", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="store.product")),
                ("variant", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="orders", to="store.variant")),
            ],
            options={"ordering": ["-created_at"]},
        ),
        migrations.CreateModel(
            name="OrderStatusHistory",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("status", models.CharField(choices=[("NEW","جديد"),("CONTACTED","تم التواصل"),("CONFIRMED","مؤكد"),("PREPARING","قيد التحضير"),("SHIPPED","تم الشحن"),("OUT_FOR_DELIVERY","قيد التوصيل"),("DELIVERED","تم التسليم"),("CANCELED","ملغي")], max_length=20)),
                ("note", models.CharField(blank=True, max_length=255)),
                ("changed_at", models.DateTimeField(auto_now_add=True)),
                ("changed_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ("order", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="history", to="orders.order")),
            ],
            options={"ordering": ["changed_at"]},
        ),
    ]