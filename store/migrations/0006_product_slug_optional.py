from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ("store", "0004_remove_product_discount_percent_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="product",
            name="slug",
            field=models.SlugField(blank=True, max_length=180, null=True, unique=True),
        ),
    ]