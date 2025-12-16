# Step 3: Make slug field unique

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0009_populate_recipient_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='awardrecipient',
            name='slug',
            field=models.SlugField(blank=True, help_text='Auto-generated from name and year', max_length=150, unique=True),
        ),
    ]
