# Generated by Django 4.2.7 on 2023-12-11 09:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0010_alter_task_due_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="due_date",
            field=models.DateField(default=datetime.date(2023, 12, 14)),
        ),
    ]
