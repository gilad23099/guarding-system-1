# models.py
from django.db import models

class Guard(models.Model):
    name = models.CharField(max_length=100)
    unavailable_hours_day = models.CharField(max_length=255, null=True, blank=True)  # Use CharField
    unavailable_hours_night = models.CharField(max_length=255, null=True, blank=True)  # Use CharField
    available_shifts_day = models.CharField(max_length=255, null=True, blank=True)  # Use CharField
    available_shifts_night = models.CharField(max_length=255, null=True, blank=True) 
    last_location_in_solution=models.IntegerField(default=-1)
    total_hours_guarded=models.IntegerField(default=0)
    sequence_number = models.IntegerField(default=0)  # Default to 0 for initial migration

    def save(self, *args, **kwargs):
        if not self.pk:  # only set on new records
            max_sequence = Guard.objects.aggregate(models.Max('sequence_number'))['sequence_number__max']
            self.sequence_number = (max_sequence + 1) if max_sequence is not None else 0
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Store the current sequence number before deletion
        current_sequence = self.sequence_number
        super().delete(*args, **kwargs)  # Delete the guard

        # Adjust sequence numbers for guards with higher sequence numbers
        Guard.objects.filter(sequence_number__gt=current_sequence).update(sequence_number=models.F('sequence_number') - 1)

    def __str__(self):
            return self.name
    

class Schedule(models.Model):
    date = models.DateField()  # Date of the schedule
    shift_type = models.CharField(max_length=5, choices=[('day', 'Day'), ('night', 'Night')])
    guards = models.ManyToManyField(Guard, through='GuardShift')  # Many-to-many relationship with Guard through GuardShift

    def __str__(self):
        return f"Schedule for {self.date} ({self.shift_type})"
    

class GuardShift(models.Model):
    guard = models.ForeignKey(Guard, on_delete=models.CASCADE)
    schedule = models.ForeignKey(Schedule, on_delete=models.CASCADE)
    start_time = models.TimeField()
    end_time = models.TimeField()

    def __str__(self):
        return f"{self.guard.name}: {self.start_time} - {self.end_time}"