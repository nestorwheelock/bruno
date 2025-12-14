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


class CBPIAssessment(models.Model):
    """
    Canine Brief Pain Inventory (CBPI) - Validated cancer pain assessment.

    Reference: Brown DC, Boston RC, Coyne JC, Farrar JT. (2008). A novel approach
    to the use of animals in studies of pain: validation of the canine brief pain
    inventory in canine bone cancer. Pain Med. 9(1):133-42.
    DOI: 10.1111/j.1526-4637.2007.00325.x
    PMID: 18823385

    Scoring: 0-10 scale where 0 = no pain/interference, 10 = extreme pain/interference
    Two validated factors:
    - Pain Severity Score (PSS): average of items 1-4
    - Pain Interference Score (PIS): average of items 5-10
    """
    QOL_CHOICES = [
        (1, 'Poor'),
        (2, 'Fair'),
        (3, 'Good'),
        (4, 'Very Good'),
        (5, 'Excellent'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Pain Severity Items (0-10, 0=no pain, 10=extreme pain)
    worst_pain = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rate the pain at its worst in the last 7 days"
    )
    least_pain = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rate the pain at its least in the last 7 days"
    )
    average_pain = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rate the pain on average"
    )
    current_pain = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Rate the pain right now"
    )

    # Pain Interference Items (0-10, 0=does not interfere, 10=completely interferes)
    general_activity = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Interference with general activity"
    )
    enjoyment_of_life = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Interference with enjoyment of life"
    )
    ability_to_rise = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Interference with ability to rise to standing from lying down"
    )
    ability_to_walk = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Interference with walking"
    )
    ability_to_run = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Interference with running"
    )
    ability_to_climb = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        help_text="Interference with climbing (stairs, curbs, etc.)"
    )

    # Global QoL (1-5 categorical, does not contribute to CBPI scores)
    overall_quality_of_life = models.IntegerField(
        choices=QOL_CHOICES,
        help_text="Overall quality of life assessment"
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'CBPI Assessment'
        verbose_name_plural = 'CBPI Assessments'

    def __str__(self):
        return f"CBPI Assessment on {self.date}"

    @property
    def pain_severity_score(self):
        """Average of pain severity items (PSS). Range 0-10."""
        items = [self.worst_pain, self.least_pain, self.average_pain, self.current_pain]
        return round(sum(items) / len(items), 2)

    @property
    def pain_interference_score(self):
        """Average of pain interference items (PIS). Range 0-10."""
        items = [
            self.general_activity, self.enjoyment_of_life, self.ability_to_rise,
            self.ability_to_walk, self.ability_to_run, self.ability_to_climb
        ]
        return round(sum(items) / len(items), 2)


class CORQAssessment(models.Model):
    """
    Canine Owner-Reported Quality of Life (CORQ) Questionnaire.

    Reference: Iliopoulou MA, Kitchell BE, Yuzbasiyan-Gurkan V. (2018).
    Development and psychometric testing of the Canine Owner-Reported Quality
    of Life questionnaire, an instrument designed to measure quality of life
    in dogs with cancer. J Am Vet Med Assoc. 252(9):1073-1083.
    DOI: 10.2460/javma.252.9.1073
    PMID: 29641337

    Four validated factors with high internal consistency (Cronbach α = 0.68-0.90):
    - Vitality
    - Companionship
    - Pain
    - Mobility

    Scoring: Items scored 1-5, higher scores = better QoL
    """
    FREQUENCY_CHOICES = [
        (1, 'Never'),
        (2, 'Rarely'),
        (3, 'Sometimes'),
        (4, 'Often'),
        (5, 'Always'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Vitality Factor
    energy_level = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog has normal energy levels"
    )
    playfulness = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog is playful"
    )
    interest_in_surroundings = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog shows interest in surroundings"
    )
    appetite = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog has normal appetite"
    )

    # Companionship Factor
    seeks_attention = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog seeks attention from family"
    )
    enjoys_interaction = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog enjoys interaction with people"
    )
    greets_family = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog greets family members"
    )
    tail_wagging = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog wags tail"
    )

    # Pain Factor (reverse scored - higher frequency = worse)
    shows_pain = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog shows signs of pain"
    )
    vocalizes_pain = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog vocalizes (whines, cries) due to pain"
    )
    avoids_touch = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog avoids being touched"
    )
    pants_restless = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog pants or is restless"
    )

    # Mobility Factor
    walks_normally = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog walks normally"
    )
    rises_easily = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog rises easily from lying down"
    )
    climbs_stairs = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog can climb stairs"
    )
    jumps = models.IntegerField(
        choices=FREQUENCY_CHOICES,
        help_text="Dog can jump (on furniture, into car)"
    )

    # Global QoL VAS
    global_qol = models.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Overall quality of life (0-100 visual analog scale)"
    )

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'CORQ Assessment'
        verbose_name_plural = 'CORQ Assessments'

    def __str__(self):
        return f"CORQ Assessment on {self.date}"

    @property
    def vitality_score(self):
        """Vitality factor score. Range 4-20, higher = better."""
        items = [self.energy_level, self.playfulness, self.interest_in_surroundings, self.appetite]
        return sum(items)

    @property
    def companionship_score(self):
        """Companionship factor score. Range 4-20, higher = better."""
        items = [self.seeks_attention, self.enjoys_interaction, self.greets_family, self.tail_wagging]
        return sum(items)

    @property
    def pain_score(self):
        """Pain factor score (reverse scored). Range 4-20, higher = less pain = better."""
        items = [self.shows_pain, self.vocalizes_pain, self.avoids_touch, self.pants_restless]
        # Reverse score: 6 - item_score converts 1->5, 2->4, 3->3, 4->2, 5->1
        return sum(6 - item for item in items)

    @property
    def mobility_score(self):
        """Mobility factor score. Range 4-20, higher = better."""
        items = [self.walks_normally, self.rises_easily, self.climbs_stairs, self.jumps]
        return sum(items)

    @property
    def total_score(self):
        """Total CORQ score. Range 16-80, higher = better QoL."""
        return self.vitality_score + self.companionship_score + self.pain_score + self.mobility_score


class VCOGCTCAEEvent(models.Model):
    """
    Veterinary Cooperative Oncology Group - Common Terminology Criteria
    for Adverse Events (VCOG-CTCAE v2).

    Reference: LeBlanc AK, Atherton M, Bentley RT, et al. (2021).
    Veterinary Cooperative Oncology Group—Common Terminology Criteria for
    Adverse Events (VCOG-CTCAE v2) following investigational therapy in
    dogs and cats. Vet Comp Oncol. 19(2):311-352.
    DOI: 10.1111/vco.12677
    PMID: 33427378

    Grade 1: Asymptomatic or mild symptoms
    Grade 2: Moderate; minimal intervention indicated
    Grade 3: Severe or medically significant but not life-threatening
    Grade 4: Life-threatening consequences; urgent intervention indicated
    Grade 5: Death related to adverse event
    """
    GRADE_CHOICES = [
        (1, 'Grade 1 - Mild'),
        (2, 'Grade 2 - Moderate'),
        (3, 'Grade 3 - Severe'),
        (4, 'Grade 4 - Life-threatening'),
        (5, 'Grade 5 - Death'),
    ]

    CATEGORY_CHOICES = [
        ('gastrointestinal', 'Gastrointestinal'),
        ('hematologic', 'Hematologic/Blood'),
        ('constitutional', 'Constitutional Symptoms'),
        ('dermatologic', 'Dermatologic/Skin'),
        ('neurologic', 'Neurologic'),
        ('cardiac', 'Cardiac'),
        ('respiratory', 'Respiratory'),
        ('renal', 'Renal/Urinary'),
        ('hepatic', 'Hepatic'),
        ('immunologic', 'Immunologic'),
        ('infection', 'Infection'),
        ('other', 'Other'),
    ]

    EVENT_CHOICES = [
        # Gastrointestinal
        ('vomiting', 'Vomiting'),
        ('diarrhea', 'Diarrhea'),
        ('anorexia', 'Anorexia/Decreased appetite'),
        ('nausea', 'Nausea'),
        ('constipation', 'Constipation'),
        ('colitis', 'Colitis'),
        # Hematologic
        ('neutropenia', 'Neutropenia'),
        ('thrombocytopenia', 'Thrombocytopenia'),
        ('anemia', 'Anemia'),
        ('leukopenia', 'Leukopenia'),
        # Constitutional
        ('lethargy', 'Lethargy/Fatigue'),
        ('fever', 'Fever'),
        ('weight_loss', 'Weight loss'),
        # Dermatologic
        ('alopecia', 'Alopecia/Hair loss'),
        ('dermatitis', 'Dermatitis'),
        ('pruritus', 'Pruritus/Itching'),
        # Other common
        ('infection', 'Infection'),
        ('hemorrhage', 'Hemorrhage'),
        ('pain', 'Pain'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    event = models.CharField(max_length=30, choices=EVENT_CHOICES)
    grade = models.IntegerField(choices=GRADE_CHOICES)

    # Related treatment (optional)
    treatment = models.CharField(max_length=100, blank=True,
        help_text="Chemotherapy agent or treatment that may have caused this event")

    # Management
    intervention = models.TextField(blank=True,
        help_text="Treatment or intervention for this adverse event")
    resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(null=True, blank=True)

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'VCOG-CTCAE Event'
        verbose_name_plural = 'VCOG-CTCAE Events'

    def __str__(self):
        return f"{self.get_event_display()} (Grade {self.grade}) on {self.date}"


class TreatmentSession(models.Model):
    """
    Track chemotherapy and other treatment sessions.
    """
    TREATMENT_TYPE_CHOICES = [
        ('chemo', 'Chemotherapy'),
        ('radiation', 'Radiation therapy'),
        ('surgery', 'Surgery'),
        ('immunotherapy', 'Immunotherapy'),
        ('palliative', 'Palliative care'),
        ('other', 'Other'),
    ]

    PROTOCOL_CHOICES = [
        ('chop', 'CHOP Protocol'),
        ('cop', 'COP Protocol'),
        ('single_agent', 'Single Agent'),
        ('madison_wisconsin', 'Madison-Wisconsin Protocol'),
        ('other', 'Other'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    treatment_type = models.CharField(max_length=20, choices=TREATMENT_TYPE_CHOICES)
    protocol = models.CharField(max_length=30, choices=PROTOCOL_CHOICES, blank=True)
    agent = models.CharField(max_length=100, blank=True,
        help_text="Specific drug or agent used (e.g., Vincristine, Doxorubicin)")
    dose = models.CharField(max_length=50, blank=True,
        help_text="Dose administered")

    cycle_number = models.IntegerField(null=True, blank=True,
        help_text="Treatment cycle number")

    pre_treatment_weight = models.DecimalField(
        max_digits=5, decimal_places=2, null=True, blank=True,
        help_text="Weight in kg before treatment")

    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Treatment Session'
        verbose_name_plural = 'Treatment Sessions'

    def __str__(self):
        return f"{self.get_treatment_type_display()} - {self.agent or self.protocol} on {self.date}"
