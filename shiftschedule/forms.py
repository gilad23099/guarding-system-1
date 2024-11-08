# forms.py
from django import forms
from .models import Guard
from datetime import time,timedelta
from django.core.exceptions import ValidationError


class GuardForm(forms.ModelForm):
    class Meta:
        model = Guard
        fields = ['name', 'unavailable_hours_day', 'unavailable_hours_night']
        labels = {
            'name': 'Guard Name',  # Custom label for name
            'unavailable_hours_day': 'unavailable_hours_day',  # Custom label for shift
            'unavailable_hours_night': 'unavailable_hours_night',  # Custom label for shift
        }

class TimeForm(forms.Form):
    date = forms.DateField(
        label="Select a date",
        required=True,
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'placeholder': 'Choose a date',
                'class': 'form-field date-field'  # Add custom class
            }
        )
    )

    SHIFT_CHOICES = [
        ('day', 'Day'),
        ('night', 'Night'),
    ]
    
    shift = forms.ChoiceField(
        choices=SHIFT_CHOICES,
        label='Select a shift',
        widget=forms.RadioSelect(
            attrs={'class': 'form-field shift-field'}  # Add custom class
        ),
        required=True
    )

    start_hour = forms.IntegerField(
        label="Start hour",
        min_value=0,
        max_value=23,
        required=True,
        widget=forms.NumberInput(
            attrs={'placeholder': 'Enter start hour', 'class': 'form-field hour-field'}
        )
    )
    
    start_minute = forms.IntegerField(
        label="Start minute",
        min_value=0,
        max_value=59,
        required=True,
        widget=forms.NumberInput(
            attrs={'placeholder': 'Enter start minute', 'class': 'form-field minute-field'}
        )
    ) 

    num_hours = forms.FloatField(
        label="Hours to guard",
        min_value=0,
        max_value=17,
        required=True,
        widget=forms.NumberInput(
            attrs={'placeholder': 'Enter hours to guard', 'class': 'form-field hours-field'}
        )
    ) 

    

class UpdateGuardForm(forms.ModelForm):
    class Meta:
        model = Guard
        fields = ['unavailable_hours_day', 'unavailable_hours_night']

    
























class TimeRangeForm(forms.Form):
    start_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}), 
        label="Start Time"
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(format='%H:%M', attrs={'type': 'time'}), 
        label="End Time"
    )

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get("start_time")
        end_time = cleaned_data.get("end_time")

        if start_time and end_time and start_time >= end_time:
            raise ValidationError("End time must be after start time.")

