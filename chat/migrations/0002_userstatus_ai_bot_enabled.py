# Generated by Django 5.1.7 on 2025-05-04 12:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userstatus',
            name='ai_bot_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
