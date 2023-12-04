# Generated by Django 4.2.7 on 2023-12-02 07:47

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0005_alter_task_due_date_alter_taskassignment_task"),
    ]

    operations = [
        migrations.AddField(
            model_name="taskassignment",
            name="status",
            field=models.CharField(
                choices=[
                    ("good", "Good"),
                    ("fair", "Fair"),
                    ("needs_improvement", "Needs Improvement"),
                    ("reviewing", "Reviewing"),
                ],
                default="reviewing",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="task",
            name="due_date",
            field=models.DateField(default=datetime.date(2023, 12, 5)),
        ),
        migrations.AlterField(
            model_name="task",
            name="user_type",
            field=models.CharField(
                choices=[("teacher", "Teacher"), ("institute", "Institute")],
                max_length=20,
            ),
        ),
    ]