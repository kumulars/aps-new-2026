# Step 1: Add slug field without unique constraint

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0007_awardsindexpage_awardtype_awardrecipient'),
    ]

    operations = [
        migrations.AddField(
            model_name='awardrecipient',
            name='slug',
            field=models.SlugField(blank=True, default='', help_text='Auto-generated from name and year', max_length=150),
            preserve_default=False,
        ),
    ]
