# Generated by Django 5.1.2 on 2024-10-28 09:42

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shiftschedule", "0013_alter_guard_sequence_number"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="guard",
            name="available_hours_amount_day",
        ),
        migrations.RemoveField(
            model_name="guard",
            name="available_hours_amount_night",
        ),
        migrations.RemoveField(
            model_name="guard",
            name="remaining_hours_day",
        ),
        migrations.RemoveField(
            model_name="guard",
            name="remaining_hours_night",
        ),
    ]
