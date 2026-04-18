# Generated manually
from django.db import migrations

def seed_site(apps, schema_editor):
    Site = apps.get_model('sites', 'Site')
    # Use update_or_create to safely insert or update if exists
    Site.objects.update_or_create(
        id=1,
        defaults={'domain': 'localhost:8000', 'name': 'SIYASI NEWS'}
    )

def reverse_seed_site(apps, schema_editor):
    pass # Reversible conceptually but we don't strictly need to delete on reverse to avoid orphaned foreign keys

class Migration(migrations.Migration):

    dependencies = [
        ('News', '0005_userprofile'),
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_site, reverse_seed_site),
    ]
