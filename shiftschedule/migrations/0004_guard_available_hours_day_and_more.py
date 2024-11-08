# Generated by Django 5.1.2 on 2024-10-19 11:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shiftschedule", "0003_alter_availability_unique_together_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="guard",
            name="available_hours_day",
            field=models.JSONField(default=-1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="guard",
            name="available_hours_night",
            field=models.JSONField(default=-1),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name="Schedule",
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
                ("shift_time", models.DateTimeField()),
                ("duration", models.DurationField()),
                ("shift_type", models.CharField(max_length=10)),
                (
                    "guard",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="shiftschedule.guard",
                    ),
                ),
            ],
        ),
    ]
