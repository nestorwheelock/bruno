from django.db import models


class Donor(models.Model):
    """Track potential and actual donors for Bruno's fundraiser."""

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('es', 'Spanish'),
        ('other', 'Other'),
    ]

    INCOME_SCALE_CHOICES = [
        (1, '1 - Low income'),
        (2, '2 - Below average'),
        (3, '3 - Average'),
        (4, '4 - Above average'),
        (5, '5 - High income'),
    ]

    CONTACT_METHOD_CHOICES = [
        ('email', 'Email'),
        ('whatsapp', 'WhatsApp'),
        ('facebook', 'Facebook Messenger'),
        ('sms', 'SMS'),
        ('phone', 'Phone Call'),
        ('other', 'Other'),
    ]

    # Basic Info
    full_name = models.CharField(max_length=200)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100)
    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, default='en')

    # Contact Info
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True, help_text="Include country code, e.g. +1 555-123-4567")
    preferred_contact = models.CharField(max_length=20, choices=CONTACT_METHOD_CHOICES, default='email')

    # Financial
    income_scale = models.IntegerField(choices=INCOME_SCALE_CHOICES, default=3,
                                        help_text="Estimated income level 1-5")

    # Engagement
    donation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                          help_text="Total donation amount in USD")
    donation_date = models.DateField(null=True, blank=True)
    has_shared = models.BooleanField(default=False, help_text="Has shared the fundraiser post")
    share_date = models.DateField(null=True, blank=True)

    # Communication tracking
    last_contacted = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Notes about this donor")

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-donation_amount', '-created_at']

    def __str__(self):
        return f"{self.full_name} ({self.country})"

    @property
    def has_donated(self):
        return self.donation_amount > 0

    @property
    def contact_info(self):
        """Return primary contact method and value."""
        if self.preferred_contact == 'whatsapp' and self.phone:
            return f"WhatsApp: {self.phone}"
        elif self.preferred_contact == 'email' and self.email:
            return f"Email: {self.email}"
        elif self.phone:
            return f"Phone: {self.phone}"
        elif self.email:
            return f"Email: {self.email}"
        return "No contact info"
