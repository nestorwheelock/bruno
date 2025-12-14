from django.contrib import admin
from .models import DailyEntry, Medication, MedicationDose, LymphNodeMeasurement


@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'good_day', 'happiness_score', 'overall_score', 'user']
    list_filter = ['good_day', 'date']
    date_hierarchy = 'date'


@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'dosage', 'frequency', 'active']
    list_filter = ['active', 'frequency']


@admin.register(MedicationDose)
class MedicationDoseAdmin(admin.ModelAdmin):
    list_display = ['medication', 'given_at', 'user']
    list_filter = ['medication', 'given_at']


@admin.register(LymphNodeMeasurement)
class LymphNodeMeasurementAdmin(admin.ModelAdmin):
    list_display = ['date', 'status', 'mandibular_left', 'mandibular_right', 'popliteal_left', 'popliteal_right']
    list_filter = ['status', 'date']
    date_hierarchy = 'date'
