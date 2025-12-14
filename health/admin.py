from django.contrib import admin
from .models import (
    DailyEntry, Medication, MedicationDose, LymphNodeMeasurement,
    CBPIAssessment, CORQAssessment, VCOGCTCAEEvent, TreatmentSession,
    DogProfile, Food, Meal, MealItem, SupplementDose, DailyNutritionSummary
)


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


@admin.register(CBPIAssessment)
class CBPIAssessmentAdmin(admin.ModelAdmin):
    list_display = ['date', 'pain_severity_score', 'pain_interference_score', 'overall_quality_of_life', 'user']
    list_filter = ['overall_quality_of_life', 'date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Assessment Info', {
            'fields': ('user', 'date')
        }),
        ('Pain Severity (0-10, 0=no pain)', {
            'fields': ('worst_pain', 'least_pain', 'average_pain', 'current_pain')
        }),
        ('Pain Interference (0-10, 0=no interference)', {
            'fields': ('general_activity', 'enjoyment_of_life', 'ability_to_rise',
                      'ability_to_walk', 'ability_to_run', 'ability_to_climb')
        }),
        ('Quality of Life', {
            'fields': ('overall_quality_of_life', 'notes')
        }),
    )


@admin.register(CORQAssessment)
class CORQAssessmentAdmin(admin.ModelAdmin):
    list_display = ['date', 'vitality_score', 'companionship_score', 'pain_score', 'mobility_score', 'total_score', 'global_qol']
    list_filter = ['date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Assessment Info', {
            'fields': ('user', 'date')
        }),
        ('Vitality (1-5, higher=better)', {
            'fields': ('energy_level', 'playfulness', 'interest_in_surroundings', 'appetite')
        }),
        ('Companionship (1-5, higher=better)', {
            'fields': ('seeks_attention', 'enjoys_interaction', 'greets_family', 'tail_wagging')
        }),
        ('Pain Signs (1-5, lower=better)', {
            'fields': ('shows_pain', 'vocalizes_pain', 'avoids_touch', 'pants_restless')
        }),
        ('Mobility (1-5, higher=better)', {
            'fields': ('walks_normally', 'rises_easily', 'climbs_stairs', 'jumps')
        }),
        ('Overall', {
            'fields': ('global_qol', 'notes')
        }),
    )


@admin.register(VCOGCTCAEEvent)
class VCOGCTCAEEventAdmin(admin.ModelAdmin):
    list_display = ['date', 'category', 'event', 'grade', 'resolved', 'user']
    list_filter = ['category', 'grade', 'resolved', 'date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Event Info', {
            'fields': ('user', 'date', 'category', 'event', 'grade')
        }),
        ('Treatment Context', {
            'fields': ('treatment',)
        }),
        ('Management', {
            'fields': ('intervention', 'resolved', 'resolved_date', 'notes')
        }),
    )


@admin.register(TreatmentSession)
class TreatmentSessionAdmin(admin.ModelAdmin):
    list_display = ['date', 'treatment_type', 'protocol', 'agent', 'cycle_number', 'user']
    list_filter = ['treatment_type', 'protocol', 'date']
    date_hierarchy = 'date'


@admin.register(DogProfile)
class DogProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'weight_kg', 'target_weight_kg', 'user', 'updated_at']
    readonly_fields = ['daily_food_min_g', 'daily_food_max_g', 'daily_calcium_min_mg',
                      'daily_calcium_max_mg', 'daily_omega3_min_mg', 'daily_omega3_max_mg']
    fieldsets = (
        ('Profile', {
            'fields': ('user', 'name', 'weight_kg', 'target_weight_kg')
        }),
        ('Calculated Daily Targets', {
            'fields': ('daily_food_min_g', 'daily_food_max_g',
                      'daily_calcium_min_mg', 'daily_calcium_max_mg',
                      'daily_omega3_min_mg', 'daily_omega3_max_mg'),
            'description': 'Auto-calculated based on weight'
        }),
    )


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'status', 'calories_per_100g', 'protein_g_per_100g',
                   'fat_g_per_100g', 'carbs_g_per_100g']
    list_filter = ['category', 'status']
    search_fields = ['name']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'category', 'status')
        }),
        ('Nutrition per 100g', {
            'fields': ('calories_per_100g', 'protein_g_per_100g', 'fat_g_per_100g', 'carbs_g_per_100g')
        }),
        ('Omega-3 & Calcium', {
            'fields': ('epa_mg_per_100g', 'dha_mg_per_100g', 'calcium_mg_per_100g')
        }),
        ('Usage Guidelines', {
            'fields': ('max_per_day', 'max_per_week', 'notes', 'warning')
        }),
    )


class MealItemInline(admin.TabularInline):
    model = MealItem
    extra = 1


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['date', 'meal_type', 'time', 'appetite', 'total_grams', 'user']
    list_filter = ['meal_type', 'appetite', 'date']
    date_hierarchy = 'date'
    inlines = [MealItemInline]


@admin.register(SupplementDose)
class SupplementDoseAdmin(admin.ModelAdmin):
    list_display = ['date', 'supplement_type', 'product_name', 'dose_amount', 'user']
    list_filter = ['supplement_type', 'date']
    date_hierarchy = 'date'


@admin.register(DailyNutritionSummary)
class DailyNutritionSummaryAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_food_g', 'total_protein_g', 'total_fat_g', 'total_carbs_g',
                   'total_calcium_mg', 'total_omega3_mg', 'multivitamin_given']
    list_filter = ['carbs_warning', 'calcium_low', 'omega3_low', 'date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Date & User', {
            'fields': ('user', 'date')
        }),
        ('Food Totals', {
            'fields': ('total_food_g', 'total_protein_g', 'total_fat_g', 'total_carbs_g', 'meals_count')
        }),
        ('Supplement Totals', {
            'fields': ('total_calcium_mg', 'total_omega3_mg', 'multivitamin_given')
        }),
        ('Counts', {
            'fields': ('eggs_count', 'tuna_servings')
        }),
        ('Warnings', {
            'fields': ('carbs_warning', 'calcium_low', 'omega3_low', 'food_low', 'eggs_warning', 'tuna_warning')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
