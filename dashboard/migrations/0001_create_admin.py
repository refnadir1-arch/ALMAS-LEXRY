from django.db import migrations
from django.contrib.auth.hashers import make_password

def create_superuser(apps, schema_editor):
    User = apps.get_model('auth', 'User')

    if not User.objects.filter(username='superadmin').exists():
        User.objects.create(
            username='superadmin',
            email='admin@example.com',
            password=make_password('Admin12345'),
            is_staff=True,
            is_superuser=True,
            is_active=True,
        )

class Migration(migrations.Migration):

    dependencies = [
        ('auth', '__latest__'),
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]