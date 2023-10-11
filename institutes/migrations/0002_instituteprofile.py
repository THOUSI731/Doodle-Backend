# Generated by Django 4.2.6 on 2023-10-10 05:12

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("institutes", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="InstituteProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "user",
                    models.OneToOneField(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="institute_profile",
                        to="institutes.institute",
                    ),
                ),
            ],
        ),
    ]