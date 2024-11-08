# Generated by Django 5.1.2 on 2024-11-01 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shiftschedule", "0017_remove_guard_hours_of_shift"),
    ]

    operations = [
        migrations.AlterField(
            model_name="guard",
            name="available_hours_day",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name="guard",
            name="available_hours_night",
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
    ]
