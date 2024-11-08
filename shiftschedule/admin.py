from django.contrib import admin
from .models import Guard,Schedule,GuardShift

# Register your models here.

admin.site.register(Guard)

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['date', 'shift_type']

@admin.register(GuardShift)
class GuardShiftAdmin(admin.ModelAdmin):
    list_display = ['guard', 'schedule', 'start_time', 'end_time']


