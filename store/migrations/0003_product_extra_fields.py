from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("store", "0002_alter_category_options_alter_product_options_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="product",
            name="compare_at_price_dzd",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="السعر قبل التخفيض"),
        ),
        migrations.AddField(
            model_name="product",
            name="cost_price_dzd",
            field=models.PositiveIntegerField(blank=True, null=True, verbose_name="سعر التكلفة"),
        ),
        migrations.AddField(
            model_name="product",
            name="video_url",
            field=models.URLField(blank=True, default="", verbose_name="رابط الفيديو"),
        ),
        migrations.AddField(
            model_name="product",
            name="sku",
            field=models.CharField(blank=True, default="", max_length=120, verbose_name="SKU"),
        ),
        migrations.AddField(
            model_name="product",
            name="seo_title",
            field=models.CharField(blank=True, default="", max_length=180, verbose_name="عنوان SEO"),
        ),
        migrations.AddField(
            model_name="product",
            name="seo_description",
            field=models.TextField(blank=True, default="", verbose_name="وصف SEO"),
        ),
    ]