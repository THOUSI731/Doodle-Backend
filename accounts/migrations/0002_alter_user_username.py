# Generated by Django 4.2.6 on 2023-10-10 06:31

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="username",
            field=models.CharField(blank=True, max_length=20, null=True, unique=True),
        ),
    ]
