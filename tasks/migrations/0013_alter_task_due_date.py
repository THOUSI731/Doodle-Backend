# Generated by Django 4.2.7 on 2023-12-18 09:40

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0012_alter_task_due_date"),
    ]

    operations = [
        migrations.AlterField(
            model_name="task",
            name="due_date",
            field=models.DateField(default=datetime.date(2023, 12, 21)),
        ),
    ]
