from django.contrib import admin
from .models import (
    DailyEntry, Medication, MedicationDose, LymphNodeMeasurement,
    CBPIAssessment, CORQAssessment, VCOGCTCAEEvent, TreatmentSession,
    DogProfile, Food, Meal, MealItem, SupplementDose, DailyNutritionSummary,
    SiteSettings, MedicalRecord, LabValue,
    Provider, TimelineEntry, TimelineAttachment
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
    list_display = ['date', 'source', 'status', 'mandibular_left', 'mandibular_right', 'popliteal_left', 'popliteal_right']
    list_filter = ['source', 'status', 'date']
    date_hierarchy = 'date'


@admin.register(CBPIAssessment)
class CBPIAssessmentAdmin(admin.ModelAdmin):
    list_display = ['date', 'source', 'pain_severity_score', 'pain_interference_score', 'overall_quality_of_life', 'user']
    list_filter = ['source', 'overall_quality_of_life', 'date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Assessment Info', {
            'fields': ('user', 'date', 'source')
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
    list_display = ['date', 'source', 'vitality_score', 'companionship_score', 'pain_score', 'mobility_score', 'total_score', 'global_qol']
    list_filter = ['source', 'date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Assessment Info', {
            'fields': ('user', 'date', 'source')
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
    list_display = ['date', 'source', 'category', 'event', 'grade', 'resolved', 'user']
    list_filter = ['source', 'category', 'grade', 'resolved', 'date']
    date_hierarchy = 'date'
    fieldsets = (
        ('Event Info', {
            'fields': ('user', 'date', 'source', 'category', 'event', 'grade')
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
    list_display = ['date', 'source', 'treatment_type', 'protocol', 'agent', 'cycle_number', 'user']
    list_filter = ['source', 'treatment_type', 'protocol', 'date']
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


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'enable_ai_parsing', 'updated_at']

    def has_add_permission(self, request):
        # Only allow one instance
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False


class LabValueInline(admin.TabularInline):
    model = LabValue
    extra = 1
    fields = ['test_name', 'value', 'unit', 'reference_low', 'reference_high', 'is_abnormal']


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = ['date', 'record_type', 'source', 'title', 'clinic_name', 'ai_parsed', 'user']
    list_filter = ['record_type', 'source', 'ai_parsed', 'date']
    date_hierarchy = 'date'
    search_fields = ['title', 'clinic_name', 'veterinarian']
    inlines = [LabValueInline]
    fieldsets = (
        ('Record Info', {
            'fields': ('user', 'date', 'record_type', 'title', 'file')
        }),
        ('Source', {
            'fields': ('source', 'clinic_name', 'veterinarian')
        }),
        ('AI Parsing', {
            'fields': ('ai_parsed', 'ai_extracted_text', 'ai_parsed_at'),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )
    readonly_fields = ['ai_parsed_at', 'file_type']


@admin.register(LabValue)
class LabValueAdmin(admin.ModelAdmin):
    list_display = ['date', 'test_name', 'value', 'unit', 'is_abnormal', 'is_critical', 'source', 'user']
    list_filter = ['test_name', 'is_abnormal', 'is_critical', 'source', 'date']
    date_hierarchy = 'date'
    search_fields = ['test_name', 'custom_test_name']
    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'medical_record', 'date', 'source')
        }),
        ('Test Results', {
            'fields': ('test_name', 'custom_test_name', 'value', 'unit')
        }),
        ('Reference Range', {
            'fields': ('reference_low', 'reference_high', 'is_abnormal', 'is_critical')
        }),
        ('AI', {
            'fields': ('ai_extracted',),
            'classes': ('collapse',)
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


class TimelineAttachmentInline(admin.TabularInline):
    model = TimelineAttachment
    extra = 1
    fields = ['file', 'file_type', 'title', 'description']


@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['name', 'clinic_name', 'location', 'specialty', 'trust_rating']
    list_filter = ['trust_rating', 'specialty']
    search_fields = ['name', 'clinic_name', 'location']
    fieldsets = (
        ('Basic Info', {
            'fields': ('name', 'clinic_name', 'location')
        }),
        ('Contact', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Professional', {
            'fields': ('specialty', 'credentials')
        }),
        ('Trust Assessment', {
            'fields': ('trust_rating', 'issues')
        }),
        ('Notes', {
            'fields': ('notes',)
        }),
    )


@admin.register(TimelineEntry)
class TimelineEntryAdmin(admin.ModelAdmin):
    list_display = ['date', 'time', 'entry_type', 'title', 'provider', 'bruno_mood', 'user']
    list_filter = ['entry_type', 'bruno_mood', 'provider', 'date']
    date_hierarchy = 'date'
    search_fields = ['title', 'content', 'tags']
    inlines = [TimelineAttachmentInline]
    fieldsets = (
        ('When', {
            'fields': ('user', 'date', 'time')
        }),
        ('What', {
            'fields': ('entry_type', 'title', 'content')
        }),
        ('Context', {
            'fields': ('provider', 'bruno_mood', 'tags')
        }),
    )


@admin.register(TimelineAttachment)
class TimelineAttachmentAdmin(admin.ModelAdmin):
    list_display = ['timeline_entry', 'file_type', 'title', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['title', 'description']
