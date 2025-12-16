# Step 2: Populate slugs for existing records

from django.db import migrations
from django.utils.text import slugify


def generate_slugs(apps, schema_editor):
    """Generate slugs for all existing AwardRecipient records."""
    AwardRecipient = apps.get_model('home', 'AwardRecipient')
    for recipient in AwardRecipient.objects.all():
        base_slug = slugify(f"{recipient.first_name}-{recipient.last_name}-{recipient.year}")
        slug = base_slug
        counter = 2
        while AwardRecipient.objects.filter(slug=slug).exclude(pk=recipient.pk).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        recipient.slug = slug
        recipient.save()


def reverse_slugs(apps, schema_editor):
    """Clear all slugs (for reverse migration)."""
    AwardRecipient = apps.get_model('home', 'AwardRecipient')
    AwardRecipient.objects.all().update(slug='')


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_awardrecipient_slug'),
    ]

    operations = [
        migrations.RunPython(generate_slugs, reverse_slugs),
    ]
