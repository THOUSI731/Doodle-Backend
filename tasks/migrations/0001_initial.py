# Generated by Django 4.2.6 on 2023-11-22 16:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Task",
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
                ("title", models.CharField(max_length=50)),
                ("description", models.TextField(blank=True, null=True)),
                (
                    "user_type",
                    models.CharField(
                        choices=[
                            ("teacher", "Teacher"),
                            ("institute", "Institute"),
                            ("student", "Student"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "task_type",
                    models.CharField(
                        choices=[("individual", "Individual"), ("batch", "Batch")],
                        max_length=20,
                    ),
                ),
                ("task_url", models.URLField(blank=True, null=True)),
                (
                    "document",
                    models.FileField(
                        blank=True, null=True, upload_to="task_documents/"
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assigned_by",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="task_assigned_by",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="TaskAssignment",
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
                ("submitted_url", models.URLField(blank=True, null=True)),
                (
                    "submitted_document",
                    models.FileField(
                        blank=True, null=True, upload_to="task_documents/"
                    ),
                ),
                ("feedback", models.TextField(blank=True, null=True)),
                ("is_completed", models.BooleanField(default=False)),
                ("is_submitted", models.BooleanField(default=False)),
                (
                    "task",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="tasks.task"
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="task",
            name="assigned_to",
            field=models.ManyToManyField(
                related_name="task_assigned_to",
                through="tasks.TaskAssignment",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
    ]
