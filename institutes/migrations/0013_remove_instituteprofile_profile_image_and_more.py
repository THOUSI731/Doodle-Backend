# Generated by Django 4.2.7 on 2023-12-18 09:40

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("institutes", "0012_alter_batch_due_date_alter_batch_scheduled_date_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="instituteprofile",
            name="profile_image",
        ),
        migrations.AddField(
            model_name="instituteprofile",
            name="profile_picture",
            field=models.URLField(blank=True, null=True),
        ),
    ]
