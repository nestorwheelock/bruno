# Bruno Health Tracker

A Django web application for tracking canine cancer treatment quality-of-life metrics using **validated, peer-reviewed assessment instruments** from veterinary oncology research.

Designed for mobile-first use by family members and veterinary teams monitoring dogs undergoing lymphoma treatment.

## Validated Assessment Instruments

This application implements three scientifically validated assessment tools used in veterinary oncology:

### 1. Canine Brief Pain Inventory (CBPI)

The gold standard for cancer pain assessment in dogs.

**Two Validated Factors:**
- **Pain Severity Score (PSS):** Average of 4 pain intensity items (0-10 scale)
- **Pain Interference Score (PIS):** Average of 6 functional interference items (0-10 scale)

> Brown DC, Boston RC, Coyne JC, Farrar JT. A novel approach to the use of animals in studies of pain: validation of the canine brief pain inventory in canine bone cancer. *Pain Medicine*. 2008;9(1):133-142. doi:[10.1111/j.1526-4637.2007.00325.x](https://doi.org/10.1111/j.1526-4637.2007.00325.x). PMID: [18823385](https://pubmed.ncbi.nlm.nih.gov/18823385/)

**Psychometric Properties:**
- Internal consistency: Cronbach's α = 0.95 (severity), 0.93 (interference)
- Test-retest reliability: κ = 0.73 (severity), 0.65 (interference)
- Validated against human Brief Pain Inventory in bone cancer model

### 2. Canine Owner-Reported Quality of Life (CORQ)

A psychometrically tested questionnaire specifically designed to measure quality of life in dogs with cancer.

**Four Validated Factors:**
- **Vitality:** Energy, playfulness, interest, appetite
- **Companionship:** Social engagement, interaction, greeting behavior
- **Pain:** Signs of discomfort (reverse scored)
- **Mobility:** Walking, rising, climbing, jumping ability

> Iliopoulou MA, Kitchell BE, Yuzbasiyan-Gurkan V. Development and psychometric testing of the Canine Owner-Reported Quality of Life questionnaire, an instrument designed to measure quality of life in dogs with cancer. *Journal of the American Veterinary Medical Association*. 2018;252(9):1073-1083. doi:[10.2460/javma.252.9.1073](https://doi.org/10.2460/javma.252.9.1073). PMID: [29641337](https://pubmed.ncbi.nlm.nih.gov/29641337/)

**Psychometric Properties:**
- Internal consistency: Cronbach's α = 0.68-0.90 across factors
- Correlation with global QoL: r = 0.49-0.71
- Good test-retest reliability and responsiveness to change

### 3. VCOG-CTCAE v2 (Adverse Events)

The Veterinary Cooperative Oncology Group Common Terminology Criteria for Adverse Events - the standard grading system for treatment-related adverse events in veterinary oncology.

**Grading Scale:**
- **Grade 1:** Asymptomatic or mild symptoms
- **Grade 2:** Moderate; minimal intervention indicated
- **Grade 3:** Severe or medically significant but not life-threatening
- **Grade 4:** Life-threatening consequences
- **Grade 5:** Death related to adverse event

> LeBlanc AK, Atherton M, Bentley RT, et al. Veterinary Cooperative Oncology Group—Common Terminology Criteria for Adverse Events (VCOG-CTCAE v2) following investigational therapy in dogs and cats. *Veterinary and Comparative Oncology*. 2021;19(2):311-352. doi:[10.1111/vco.12677](https://doi.org/10.1111/vco.12677). PMID: [33427378](https://pubmed.ncbi.nlm.nih.gov/33427378/)

### 4. Cancer-Supportive Nutrition Module

Evidence-based nutrition tracking for homemade zero-carbohydrate cancer diets based on the Warburg effect (cancer cells preferentially metabolize glucose).

**Features:**
- **Food Database:** Pre-populated with approved, limited, and blocked foods
- **Meal Tracking:** Log daily meals with automatic macro calculation
- **Supplement Tracking:** Calcium, fish oil (EPA/DHA), multivitamin logging
- **Personalized Targets:** Calculate daily food/supplement needs based on body weight
- **Meal Planning:** Sample meal plans with portion sizes and preparation guides
- **Warnings:** Automatic alerts for carbohydrate intake and supplement deficiencies

**Nutritional Targets:**
- **Macros:** High protein (30-45%), high fat (30-50%), zero carbohydrates
- **Omega-3:** 50-100 mg EPA+DHA per kg body weight daily
- **Calcium:** 50-60 mg per kg body weight daily

> Ogilvie GK, Vail DM, Wheeler SL, et al. Effects of chemotherapy and remission on carbohydrate metabolism in dogs with lymphoma. *Cancer*. 1992;69(1):233-238. [PubMed](https://pubmed.ncbi.nlm.nih.gov/1727668/)

> Ogilvie GK, Fettman MJ, Mallinckrodt CH, et al. Effect of fish oil, arginine, and doxorubicin chemotherapy on remission and survival time for dogs with lymphoma: a double-blind, randomized placebo-controlled study. *Cancer*. 2000;88(8):1916-1928. [PubMed](https://pubmed.ncbi.nlm.nih.gov/10760765/)

## Additional Features

### Case Journal / Timeline
A comprehensive medical journal system for documenting Bruno's treatment journey:
- **Timeline Entries:** Chronological record of vet visits, lab results, treatments, symptoms, concerns, and milestones
- **Entry Types:** Vet Visit, Lab Result, Imaging, Procedure, Treatment, Medication Change, Symptom, Communication, Milestone, Concern, Research
- **Rich Content:** Full narrative entries with mood tracking, file attachments (photos, videos, PDFs), and tags
- **Provider Integration:** Link entries to healthcare providers with trust ratings
- **Navigation:** Swipe-enabled prev/next navigation between entries, keyboard shortcuts
- **Mobile-First:** Optimized for quick entries during vet visits

### Provider Tracking
Track all veterinarians, clinics, and specialists involved in care:
- **Trust Ratings:** 1-5 star system with color-coded ratings
- **Contact Info:** Phone, email, website, location
- **Credentials:** Track DVM, DACVIM, and other certifications
- **Issues/Concerns:** Document any problems or reasons for distrust
- **Notes:** General notes about each provider

### Core Tracking Features
- **Daily Health Tracking:** Record quality-of-life metrics including mood, appetite, energy, and comfort levels
- **Medication Management:** Track medications and record doses given
- **Lymph Node Measurements:** Monitor node sizes over time (mandibular, popliteal)
- **Treatment Sessions:** Log chemotherapy cycles, protocols (CHOP, COP, Madison-Wisconsin), and agents
- **History & Trends:** View summaries and track progress over time
- **Multi-User Support:** Multiple family members/caregivers can log in and track simultaneously
- **Spanish Language Support:** Full i18n with Spanish translations

## Tech Stack

- Django 6.0
- PostgreSQL (Docker) / SQLite (development)
- Mobile-first responsive design
- Docker & Docker Compose
- Gunicorn + WhiteNoise

## Quick Start

```bash
# Clone the repository
git clone https://github.com/nestorwheelock/bruno.git
cd bruno

# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

## Docker Deployment

```bash
docker-compose up -d
```

The app will be available at `http://localhost:1080`

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=health --cov-report=term-missing
```

## Project Structure

```
bruno/
├── brunosite/              # Django project settings
├── health/                 # Main health tracking app
│   ├── models.py           # All data models including validated instruments
│   │   ├── DailyEntry      # Daily QoL tracking
│   │   ├── CBPIAssessment  # Validated pain assessment
│   │   ├── CORQAssessment  # Validated QoL questionnaire
│   │   ├── VCOGCTCAEEvent  # Adverse events (CTCAE grading)
│   │   ├── TreatmentSession # Chemo/treatment tracking
│   │   ├── Medication      # Medication management
│   │   ├── MedicationDose  # Dose recording
│   │   ├── LymphNodeMeasurement # Node size tracking
│   │   ├── DogProfile      # Weight-based nutrition targets
│   │   ├── Food            # Food database with status
│   │   ├── Meal / MealItem # Meal logging
│   │   ├── SupplementDose  # Supplement tracking
│   │   ├── DailyNutritionSummary # Daily totals/warnings
│   │   ├── Provider        # Healthcare provider tracking
│   │   ├── TimelineEntry   # Case journal entries
│   │   └── TimelineAttachment # File attachments for entries
│   ├── fixtures/foods.json # Pre-populated food database
│   ├── views.py            # All views
│   ├── urls.py             # URL routing
│   └── tests.py            # Test suite (94 tests)
├── planning/               # Research documentation
│   └── NUTRITION_RESEARCH.md  # Nutrition research citations
├── fundraiser/             # Public fundraising page
├── templates/              # HTML templates
├── static/                 # Static assets
└── docker-compose.yml      # Docker configuration
```

## Scientific References

### Primary Instruments

1. **CBPI Validation:**
   Brown DC, Boston RC, Coyne JC, Farrar JT. A novel approach to the use of animals in studies of pain: validation of the canine brief pain inventory in canine bone cancer. *Pain Med*. 2008;9(1):133-42. [PubMed](https://pubmed.ncbi.nlm.nih.gov/18823385/)

2. **CORQ Development:**
   Iliopoulou MA, Kitchell BE, Yuzbasiyan-Gurkan V. Development and psychometric testing of the Canine Owner-Reported Quality of Life questionnaire. *J Am Vet Med Assoc*. 2018;252(9):1073-1083. [PubMed](https://pubmed.ncbi.nlm.nih.gov/29641337/)

3. **VCOG-CTCAE v2:**
   LeBlanc AK, et al. Veterinary Cooperative Oncology Group—Common Terminology Criteria for Adverse Events (VCOG-CTCAE v2). *Vet Comp Oncol*. 2021;19(2):311-352. [PubMed](https://pubmed.ncbi.nlm.nih.gov/33427378/) | [Full Text (PMC)](https://pmc.ncbi.nlm.nih.gov/articles/PMC8248125/)

### Nutrition Research

4. **Carbohydrate Metabolism in Canine Lymphoma:**
   Ogilvie GK, Vail DM, Wheeler SL, et al. Effects of chemotherapy and remission on carbohydrate metabolism in dogs with lymphoma. *Cancer*. 1992;69(1):233-238. [PubMed](https://pubmed.ncbi.nlm.nih.gov/1727668/)

5. **Fish Oil and Survival in Canine Lymphoma:**
   Ogilvie GK, Fettman MJ, Mallinckrodt CH, et al. Effect of fish oil, arginine, and doxorubicin chemotherapy on remission and survival time for dogs with lymphoma: a double-blind, randomized placebo-controlled study. *Cancer*. 2000;88(8):1916-1928. [PubMed](https://pubmed.ncbi.nlm.nih.gov/10760765/)

6. **Lactate Metabolism in Canine Lymphoma:**
   Vail DM, Ogilvie GK, Wheeler SL, et al. Alterations in carbohydrate metabolism in canine lymphoma. *J Vet Intern Med*. 1990;4(1):8-14. [PubMed](https://pubmed.ncbi.nlm.nih.gov/2407842/)

7. **Dietary Fat and Canine Lymphoma:**
   Ogilvie GK, Ford RB, Vail DM, et al. Alterations in lipoprotein profiles in dogs with lymphoma. *J Vet Intern Med*. 1994;8(1):62-66. [PubMed](https://pubmed.ncbi.nlm.nih.gov/9055974/)

### Supporting Literature

8. **QoL Measurement in Veterinary Oncology:**
   Giuffrida MA, Kerrigan SM. Quality of life measurement in prospective studies of cancer treatments in dogs and cats. *J Vet Intern Med*. 2014;28(6):1824-29. [PubMed](https://pubmed.ncbi.nlm.nih.gov/25308707/) | [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4895614/)

9. **CBPI International Validation:**
   Enomoto M, et al. Linguistic Validation of the Canine Brief Pain Inventory (CBPI) for Global Use. *Front Vet Sci*. 2021;8:777261. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC8666957/)

10. **QoL Assessment Evidence Review:**
    Belshaw Z, et al. Quality of life assessment in domestic dogs: An evidence-based rapid review. *Vet J*. 2015;206(2):203-12. [PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC4641869/)

## Clinical Use

This application is intended to:
- Facilitate systematic quality-of-life monitoring using validated instruments
- Support communication between pet owners and veterinary oncology teams
- Provide longitudinal data for treatment decision-making
- Track treatment-related adverse events using standardized grading

**Note:** This tool is designed to supplement, not replace, professional veterinary care. All treatment decisions should be made in consultation with a licensed veterinarian or veterinary oncologist.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contributing

Contributions are welcome. Please ensure any additions to assessment instruments are backed by peer-reviewed research and properly cited.

## Acknowledgments

- Dr. Dorothy Cimino Brown and colleagues for the CBPI
- Dr. Maria Iliopoulou and colleagues for the CORQ
- The Veterinary Cooperative Oncology Group for the VCOG-CTCAE
- All the researchers advancing evidence-based veterinary oncology care
