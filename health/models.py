from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class DailyEntry(models.Model):
    GOOD_DAY_CHOICES = [
        ('yes', 'Yes'),
        ('mixed', 'Mixed'),
        ('no', 'No'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    good_day = models.CharField(max_length=5, choices=GOOD_DAY_CHOICES, blank=True)

    tail_body_language = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    interest_people = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    interest_environment = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    enjoyment_favorites = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    overall_spark = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )

    appetite = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    food_enjoyment = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    nausea_signs = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    weight_condition = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )

    breakfast = models.BooleanField(default=False)
    lunch = models.BooleanField(default=False)
    dinner = models.BooleanField(default=False)
    treats = models.BooleanField(default=False)

    energy_level = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    willingness_move = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    walking_comfort = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    resting_comfort = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )

    breathing_comfort = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    pain_signs = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    sleep_quality = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )
    response_touch = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(5)], null=True, blank=True
    )

    good_notes = models.TextField(blank=True)
    hard_notes = models.TextField(blank=True)
    other_notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['date']
        verbose_name_plural = 'Daily Entries'

    def __str__(self):
        return f"Entry for {self.date}"

    @property
    def happiness_score(self):
        mood_fields = [
            self.tail_body_language, self.interest_people,
            self.interest_environment, self.enjoyment_favorites, self.overall_spark
        ]
        valid = [f for f in mood_fields if f is not None]
        if valid:
            return round(sum(valid) / len(valid), 1)
        return None

    @property
    def overall_score(self):
        all_fields = [
            self.tail_body_language, self.interest_people, self.interest_environment,
            self.enjoyment_favorites, self.overall_spark, self.appetite,
            self.food_enjoyment, self.nausea_signs, self.weight_condition,
            self.energy_level, self.willingness_move, self.walking_comfort,
            self.resting_comfort, self.breathing_comfort, self.pain_signs,
            self.sleep_quality, self.response_touch
        ]
        valid = [f for f in all_fields if f is not None]
        if valid:
            return round(sum(valid) / len(valid), 1)
        return None


class Medication(models.Model):
    FREQUENCY_CHOICES = [
        ('once', 'Once daily'),
        ('twice', 'Twice daily'),
        ('three', 'Three times daily'),
        ('asNeeded', 'As needed'),
    ]

    name = models.CharField(max_length=100)
    dosage = models.CharField(max_length=50)
    frequency = models.CharField(max_length=10, choices=FREQUENCY_CHOICES)
    notes = models.TextField(blank=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.dosage})"


class MedicationDose(models.Model):
    medication = models.ForeignKey(Medication, on_delete=models.CASCADE, related_name='doses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    given_at = models.DateTimeField()
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-given_at']

    def __str__(self):
        return f"{self.medication.name} at {self.given_at}"


class LymphNodeMeasurement(models.Model):
    STATUS_CHOICES = [
        ('smaller', 'Smaller'),
        ('same', 'Same'),
        ('larger', 'Larger'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    mandibular_left = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Size in cm"
    )
    mandibular_right = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Size in cm"
    )
    popliteal_left = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Size in cm"
    )
    popliteal_right = models.DecimalField(
        max_digits=4, decimal_places=1, null=True, blank=True,
        help_text="Size in cm"
    )

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']

    def __str__(self):
        return f"Node measurement on {self.date}"
