# Generated by Django 5.1.2 on 2024-10-19 12:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("shiftschedule", "0005_alter_guard_available_hours_day_and_more"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="schedule",
            name="guard",
        ),
        migrations.RemoveField(
            model_name="shift",
            name="guard",
        ),
        migrations.DeleteModel(
            name="Availability",
        ),
        migrations.DeleteModel(
            name="Schedule",
        ),
        migrations.DeleteModel(
            name="Shift",
        ),
    ]
