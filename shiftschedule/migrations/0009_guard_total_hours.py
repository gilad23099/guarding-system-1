# Generated by Django 5.1.2 on 2024-10-27 05:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("shiftschedule", "0008_guardshift_schedule_guardshift_schedule"),
    ]

    operations = [
        migrations.AddField(
            model_name="guard",
            name="total_hours",
            field=models.IntegerField(default=0),
        ),
    ]
