from django.contrib import admin
from .models import Donor


@admin.register(Donor)
class DonorAdmin(admin.ModelAdmin):
    list_display = [
        'full_name', 'country', 'language', 'preferred_contact',
        'income_scale', 'donation_amount', 'has_donated_display',
        'has_shared', 'last_contacted'
    ]
    list_filter = [
        'country', 'language', 'preferred_contact', 'income_scale',
        'has_shared', 'donation_date'
    ]
    search_fields = ['full_name', 'email', 'phone', 'city', 'country', 'notes']
    ordering = ['-donation_amount', '-created_at']

    fieldsets = (
        ('Personal Info', {
            'fields': ('full_name', 'city', 'country', 'language')
        }),
        ('Contact Info', {
            'fields': ('email', 'phone', 'preferred_contact')
        }),
        ('Financial Profile', {
            'fields': ('income_scale',)
        }),
        ('Engagement', {
            'fields': ('donation_amount', 'donation_date', 'has_shared', 'share_date')
        }),
        ('Communication', {
            'fields': ('last_contacted', 'notes')
        }),
    )

    readonly_fields = ['created_at', 'updated_at']

    @admin.display(boolean=True, description='Donated?')
    def has_donated_display(self, obj):
        return obj.has_donated

    actions = ['mark_as_shared', 'mark_as_contacted']

    @admin.action(description="Mark selected as shared")
    def mark_as_shared(self, request, queryset):
        from django.utils import timezone
        queryset.update(has_shared=True, share_date=timezone.now().date())

    @admin.action(description="Mark selected as contacted now")
    def mark_as_contacted(self, request, queryset):
        from django.utils import timezone
        queryset.update(last_contacted=timezone.now())
