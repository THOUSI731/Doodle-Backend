# Generated by Django 4.2.7 on 2023-12-04 12:35

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("videorooms", "0002_rename_room_link_classroom_room_code"),
    ]

    operations = [
        migrations.AlterField(
            model_name="classroom",
            name="room_code",
            field=models.CharField(blank=True, max_length=30, null=True),
        ),
    ]
