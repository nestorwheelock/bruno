from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.translation import gettext as _
from django.conf import settings
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import (
    DailyEntry, Medication, MedicationDose, LymphNodeMeasurement,
    CBPIAssessment, CORQAssessment, VCOGCTCAEEvent, TreatmentSession,
    DogProfile, Food, Meal, MealItem, SupplementDose, DailyNutritionSummary,
    MedicalRecord, LabValue, SiteSettings
)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('health:tracker')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('health:tracker')
        else:
            return render(request, 'health/login.html', {'error': 'Invalid credentials'})

    return render(request, 'health/login.html')


def logout_view(request):
    logout(request)
    return redirect('health:login')


@login_required(login_url='health:login')
def tracker_view(request):
    today = date.today()
    yesterday = today - timedelta(days=1)

    entry, created = DailyEntry.objects.get_or_create(
        date=today,
        defaults={'user': request.user}
    )

    # Get yesterday's entry for pre-fill defaults (only if today is new)
    yesterday_entry = None
    if created:
        yesterday_entry = DailyEntry.objects.filter(
            date=yesterday, user=request.user
        ).first()

    # Build default values: today's value > yesterday's value > None
    rating_fields = [
        'tail_body_language', 'interest_people', 'interest_environment',
        'enjoyment_favorites', 'overall_spark', 'appetite', 'food_enjoyment',
        'nausea_signs', 'weight_condition', 'energy_level', 'willingness_move',
        'walking_comfort', 'resting_comfort', 'breathing_comfort', 'pain_signs',
        'sleep_quality', 'response_touch'
    ]

    default_values = {}
    for field in rating_fields:
        today_val = getattr(entry, field)
        if today_val is not None:
            default_values[field] = today_val
        elif yesterday_entry:
            default_values[field] = getattr(yesterday_entry, field)
        else:
            default_values[field] = None

    medications = Medication.objects.filter(active=True)

    today_doses = MedicationDose.objects.filter(
        given_at__date=today
    ).select_related('medication')

    week_ago = today - timedelta(days=7)
    recent_entries = DailyEntry.objects.filter(date__gte=week_ago)

    good_days = recent_entries.filter(good_day='yes').count()
    total_days = recent_entries.exclude(good_day='').count()
    good_day_percent = round(good_days / total_days * 100) if total_days > 0 else 0

    context = {
        'entry': entry,
        'default_values': default_values,
        'medications': medications,
        'today_doses': today_doses,
        'good_day_percent': good_day_percent,
        'total_days': total_days,
    }
    return render(request, 'health/tracker.html', context)


@login_required(login_url='health:login')
@require_POST
def save_daily_entry(request):
    today = date.today()
    entry, created = DailyEntry.objects.get_or_create(
        date=today,
        defaults={'user': request.user}
    )

    data = json.loads(request.body)

    entry.good_day = data.get('good_day', '')
    entry.tail_body_language = data.get('tail_body_language')
    entry.interest_people = data.get('interest_people')
    entry.interest_environment = data.get('interest_environment')
    entry.enjoyment_favorites = data.get('enjoyment_favorites')
    entry.overall_spark = data.get('overall_spark')
    entry.appetite = data.get('appetite')
    entry.food_enjoyment = data.get('food_enjoyment')
    entry.nausea_signs = data.get('nausea_signs')
    entry.weight_condition = data.get('weight_condition')
    entry.breakfast = data.get('breakfast', False)
    entry.lunch = data.get('lunch', False)
    entry.dinner = data.get('dinner', False)
    entry.treats = data.get('treats', False)
    entry.energy_level = data.get('energy_level')
    entry.willingness_move = data.get('willingness_move')
    entry.walking_comfort = data.get('walking_comfort')
    entry.resting_comfort = data.get('resting_comfort')
    entry.breathing_comfort = data.get('breathing_comfort')
    entry.pain_signs = data.get('pain_signs')
    entry.sleep_quality = data.get('sleep_quality')
    entry.response_touch = data.get('response_touch')
    entry.good_notes = data.get('good_notes', '')
    entry.hard_notes = data.get('hard_notes', '')
    entry.other_notes = data.get('other_notes', '')
    entry.user = request.user
    entry.save()

    return JsonResponse({'status': 'success', 'happiness_score': entry.happiness_score})


@login_required(login_url='health:login')
@require_POST
def add_medication(request):
    data = json.loads(request.body)

    med = Medication.objects.create(
        name=data['name'],
        dosage=data['dosage'],
        frequency=data.get('frequency', 'once'),
        notes=data.get('notes', '')
    )

    return JsonResponse({
        'status': 'success',
        'id': med.id,
        'name': med.name,
        'dosage': med.dosage
    })


@login_required(login_url='health:login')
@require_POST
def record_dose(request, med_id):
    medication = get_object_or_404(Medication, id=med_id)

    dose = MedicationDose.objects.create(
        medication=medication,
        user=request.user,
        given_at=timezone.now()
    )

    return JsonResponse({
        'status': 'success',
        'time': dose.given_at.strftime('%I:%M %p')
    })


@login_required(login_url='health:login')
@require_POST
def save_node_measurement(request):
    data = json.loads(request.body)
    today = date.today()

    measurement, created = LymphNodeMeasurement.objects.get_or_create(
        date=today,
        defaults={'user': request.user}
    )

    measurement.mandibular_left = data.get('mandibular_left') or None
    measurement.mandibular_right = data.get('mandibular_right') or None
    measurement.popliteal_left = data.get('popliteal_left') or None
    measurement.popliteal_right = data.get('popliteal_right') or None
    measurement.status = data.get('status', '')
    measurement.notes = data.get('notes', '')
    measurement.user = request.user
    measurement.save()

    return JsonResponse({'status': 'success'})


@login_required(login_url='health:login')
def history_view(request):
    entries = DailyEntry.objects.all()[:14]
    node_measurements = LymphNodeMeasurement.objects.all()[:10]

    week_ago = date.today() - timedelta(days=7)
    recent = DailyEntry.objects.filter(date__gte=week_ago)

    good_days = recent.filter(good_day='yes').count()
    mixed_days = recent.filter(good_day='mixed').count()
    bad_days = recent.filter(good_day='no').count()
    total = good_days + mixed_days + bad_days

    two_weeks_ago = date.today() - timedelta(days=14)
    prev_week = DailyEntry.objects.filter(date__gte=two_weeks_ago, date__lt=week_ago)
    prev_good = prev_week.filter(good_day='yes').count()
    prev_total = prev_week.exclude(good_day='').count()

    if total > 0 and prev_total > 0:
        current_pct = good_days / total
        prev_pct = prev_good / prev_total
        if current_pct > prev_pct:
            trend = 'Better'
        elif current_pct < prev_pct:
            trend = 'Worse'
        else:
            trend = 'Same'
    else:
        trend = '--'

    context = {
        'entries': entries,
        'node_measurements': node_measurements,
        'good_day_percent': round(good_days / total * 100) if total > 0 else 0,
        'total_days': total,
        'trend': trend,
    }
    return render(request, 'health/history.html', context)


@login_required(login_url='health:login')
def medications_view(request):
    medications = Medication.objects.filter(active=True)
    today = date.today()

    today_doses = MedicationDose.objects.filter(
        given_at__date=today
    ).select_related('medication')

    context = {
        'medications': medications,
        'today_doses': today_doses,
    }
    return render(request, 'health/medications.html', context)


@login_required(login_url='health:login')
def nodes_view(request):
    today = date.today()
    measurement = LymphNodeMeasurement.objects.filter(date=today).first()
    history = LymphNodeMeasurement.objects.all()[:10]

    context = {
        'measurement': measurement,
        'history': history,
    }
    return render(request, 'health/nodes.html', context)


@login_required(login_url='health:login')
def dashboard_view(request):
    """Main QoL dashboard with validated assessment summaries."""
    today = date.today()
    thirty_days_ago = today - timedelta(days=30)

    # Get today's entry
    today_entry = DailyEntry.objects.filter(date=today).first()

    # Calculate today's category scores
    # For star display: round to nearest integer (4.5+ = 5, below 4.5 = 4)
    today_scores = {
        'mood': None,
        'appetite': None,
        'energy': None,
        'pain': None,
        'overall': None,
        'mood_stars': None,
        'appetite_stars': None,
        'energy_stars': None,
        'pain_stars': None,
        'overall_stars': None,
    }
    if today_entry:
        # Mood (5 fields)
        mood_fields = [today_entry.tail_body_language, today_entry.interest_people,
                       today_entry.interest_environment, today_entry.enjoyment_favorites,
                       today_entry.overall_spark]
        mood_valid = [f for f in mood_fields if f is not None]
        if mood_valid:
            avg = sum(mood_valid) / len(mood_valid)
            today_scores['mood'] = round(avg, 1)
            today_scores['mood_stars'] = round(avg)  # Round to nearest int for stars

        # Appetite (2 fields)
        appetite_fields = [today_entry.appetite, today_entry.food_enjoyment]
        appetite_valid = [f for f in appetite_fields if f is not None]
        if appetite_valid:
            avg = sum(appetite_valid) / len(appetite_valid)
            today_scores['appetite'] = round(avg, 1)
            today_scores['appetite_stars'] = round(avg)

        # Energy (2 fields)
        energy_fields = [today_entry.energy_level, today_entry.willingness_move]
        energy_valid = [f for f in energy_fields if f is not None]
        if energy_valid:
            avg = sum(energy_valid) / len(energy_valid)
            today_scores['energy'] = round(avg, 1)
            today_scores['energy_stars'] = round(avg)

        # Pain/Comfort (2 fields - higher is better/less pain)
        pain_fields = [today_entry.pain_signs, today_entry.breathing_comfort]
        pain_valid = [f for f in pain_fields if f is not None]
        if pain_valid:
            avg = sum(pain_valid) / len(pain_valid)
            today_scores['pain'] = round(avg, 1)
            today_scores['pain_stars'] = round(avg)

        today_scores['overall'] = today_entry.overall_score
        if today_entry.overall_score:
            today_scores['overall_stars'] = round(today_entry.overall_score)

    # Get latest assessments
    latest_cbpi = CBPIAssessment.objects.first()
    latest_corq = CORQAssessment.objects.first()
    latest_node = LymphNodeMeasurement.objects.first()

    # Assessment reminders - days since last
    assessment_reminders = []
    if latest_cbpi:
        days_since_cbpi = (today - latest_cbpi.date).days
        if days_since_cbpi >= 7:
            assessment_reminders.append({
                'name': 'CBPI Pain',
                'days': days_since_cbpi,
                'overdue': days_since_cbpi > 7,
                'url': 'health:cbpi'
            })
    else:
        assessment_reminders.append({
            'name': 'CBPI Pain',
            'days': None,
            'overdue': True,
            'url': 'health:cbpi'
        })

    if latest_corq:
        days_since_corq = (today - latest_corq.date).days
        if days_since_corq >= 14:
            assessment_reminders.append({
                'name': 'CORQ QoL',
                'days': days_since_corq,
                'overdue': days_since_corq > 14,
                'url': 'health:corq'
            })
    else:
        assessment_reminders.append({
            'name': 'CORQ QoL',
            'days': None,
            'overdue': True,
            'url': 'health:corq'
        })

    if latest_node:
        days_since_nodes = (today - latest_node.date).days
        if days_since_nodes >= 7:
            assessment_reminders.append({
                'name': 'Lymph Nodes',
                'days': days_since_nodes,
                'overdue': days_since_nodes > 7,
                'url': 'health:nodes'
            })
    else:
        assessment_reminders.append({
            'name': 'Lymph Nodes',
            'days': None,
            'overdue': True,
            'url': 'health:nodes'
        })

    # Recent adverse events
    recent_events = VCOGCTCAEEvent.objects.filter(
        date__gte=thirty_days_ago
    ).order_by('-date')[:5]

    # Recent treatments
    recent_treatments = TreatmentSession.objects.filter(
        date__gte=thirty_days_ago
    ).order_by('-date')[:5]

    # Daily entry stats
    entries = DailyEntry.objects.filter(date__gte=thirty_days_ago)
    good_days = entries.filter(good_day='yes').count()
    mixed_days = entries.filter(good_day='mixed').count()
    bad_days = entries.filter(good_day='no').count()
    total_days = good_days + mixed_days + bad_days

    # Nutrition data
    today_nutrition = DailyNutritionSummary.objects.filter(date=today).first()
    dog_profile = DogProfile.objects.first()

    # Medication data
    active_meds = Medication.objects.filter(active=True)
    today_doses = MedicationDose.objects.filter(
        given_at__date=today
    ).select_related('medication')
    doses_given = {dose.medication_id for dose in today_doses}

    # Calculate trend (compare last 7 days to previous 7 days)
    seven_days_ago = today - timedelta(days=7)
    fourteen_days_ago = today - timedelta(days=14)

    recent_entries = DailyEntry.objects.filter(date__gte=seven_days_ago, date__lt=today)
    previous_entries = DailyEntry.objects.filter(date__gte=fourteen_days_ago, date__lt=seven_days_ago)

    recent_scores = [e.overall_score for e in recent_entries if e.overall_score]
    previous_scores = [e.overall_score for e in previous_entries if e.overall_score]

    trend = 'stable'
    trend_value = 0
    if recent_scores and previous_scores:
        recent_avg = sum(recent_scores) / len(recent_scores)
        previous_avg = sum(previous_scores) / len(previous_scores)
        trend_value = round(recent_avg - previous_avg, 1)
        if trend_value > 0.2:
            trend = 'improving'
        elif trend_value < -0.2:
            trend = 'declining'

    # Calculate QoL status color based on today's entry or CORQ
    qol_status = 'gray'
    qol_message = _('No entry yet today')
    if today_scores['overall']:
        score = today_scores['overall']
        if score >= 4:
            qol_status = 'green'
            qol_message = _('Great day!')
        elif score >= 3:
            qol_status = 'yellow'
            qol_message = _('Good day')
        elif score >= 2:
            qol_status = 'orange'
            qol_message = _('Difficult day')
        else:
            qol_status = 'red'
            qol_message = _('Hard day - monitor closely')
    elif latest_corq:
        total = latest_corq.total_score
        if total >= 60:
            qol_status = 'green'
            qol_message = _('Good quality of life')
        elif total >= 45:
            qol_status = 'yellow'
            qol_message = _('Fair - monitor closely')
        elif total >= 30:
            qol_status = 'orange'
            qol_message = _('Declining - consult vet')
        else:
            qol_status = 'red'
            qol_message = _('Poor - urgent consultation needed')

    context = {
        'today_entry': today_entry,
        'today_scores': today_scores,
        'latest_cbpi': latest_cbpi,
        'latest_corq': latest_corq,
        'latest_node': latest_node,
        'assessment_reminders': assessment_reminders,
        'recent_events': recent_events,
        'recent_treatments': recent_treatments,
        'good_days': good_days,
        'mixed_days': mixed_days,
        'bad_days': bad_days,
        'total_days': total_days,
        'today_nutrition': today_nutrition,
        'dog_profile': dog_profile,
        'active_meds': active_meds,
        'doses_given': doses_given,
        'trend': trend,
        'trend_value': trend_value,
        'qol_status': qol_status,
        'qol_message': qol_message,
    }
    return render(request, 'health/dashboard.html', context)


@login_required(login_url='health:login')
def api_chart_data(request):
    """API endpoint for chart data."""
    chart_type = request.GET.get('type', 'daily')
    days = int(request.GET.get('days', 30))
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    if chart_type == 'daily':
        entries = DailyEntry.objects.filter(
            date__gte=start_date
        ).order_by('date')
        data = {
            'labels': [e.date.strftime('%m/%d') for e in entries],
            'happiness': [e.happiness_score or 0 for e in entries],
            'overall': [e.overall_score or 0 for e in entries],
        }

    elif chart_type == 'cbpi':
        assessments = CBPIAssessment.objects.filter(
            date__gte=start_date
        ).order_by('date')
        data = {
            'labels': [a.date.strftime('%m/%d') for a in assessments],
            'severity': [a.pain_severity_score for a in assessments],
            'interference': [a.pain_interference_score for a in assessments],
        }

    elif chart_type == 'corq':
        assessments = CORQAssessment.objects.filter(
            date__gte=start_date
        ).order_by('date')
        data = {
            'labels': [a.date.strftime('%m/%d') for a in assessments],
            'vitality': [a.vitality_score for a in assessments],
            'companionship': [a.companionship_score for a in assessments],
            'pain': [a.pain_score for a in assessments],
            'mobility': [a.mobility_score for a in assessments],
            'total': [a.total_score for a in assessments],
        }

    elif chart_type == 'nodes':
        measurements = LymphNodeMeasurement.objects.filter(
            date__gte=start_date
        ).order_by('date')
        data = {
            'labels': [m.date.strftime('%m/%d') for m in measurements],
            'mandibular_left': [float(m.mandibular_left) if m.mandibular_left else None for m in measurements],
            'mandibular_right': [float(m.mandibular_right) if m.mandibular_right else None for m in measurements],
            'popliteal_left': [float(m.popliteal_left) if m.popliteal_left else None for m in measurements],
            'popliteal_right': [float(m.popliteal_right) if m.popliteal_right else None for m in measurements],
        }

    elif chart_type == 'events':
        events = VCOGCTCAEEvent.objects.filter(date__gte=start_date)
        grade_counts = {}
        for grade in range(1, 6):
            grade_counts[f'grade_{grade}'] = events.filter(grade=grade).count()
        category_counts = {}
        for cat, _ in VCOGCTCAEEvent.CATEGORY_CHOICES:
            category_counts[cat] = events.filter(category=cat).count()
        data = {
            'grades': grade_counts,
            'categories': category_counts,
        }

    else:
        data = {'error': 'Unknown chart type'}

    return JsonResponse(data)


@login_required(login_url='health:login')
def cbpi_view(request):
    """CBPI assessment form and history."""
    today = date.today()
    assessments = CBPIAssessment.objects.all()[:10]
    latest = assessments.first() if assessments else None

    context = {
        'assessments': assessments,
        'latest': latest,
    }
    return render(request, 'health/cbpi.html', context)


@login_required(login_url='health:login')
@require_POST
def save_cbpi(request):
    """Save CBPI assessment."""
    data = json.loads(request.body)
    today = date.today()

    assessment = CBPIAssessment.objects.create(
        user=request.user,
        date=today,
        worst_pain=data['worst_pain'],
        least_pain=data['least_pain'],
        average_pain=data['average_pain'],
        current_pain=data['current_pain'],
        general_activity=data['general_activity'],
        enjoyment_of_life=data['enjoyment_of_life'],
        ability_to_rise=data['ability_to_rise'],
        ability_to_walk=data['ability_to_walk'],
        ability_to_run=data['ability_to_run'],
        ability_to_climb=data['ability_to_climb'],
        overall_quality_of_life=data['overall_quality_of_life'],
        notes=data.get('notes', '')
    )

    return JsonResponse({
        'status': 'success',
        'pain_severity_score': assessment.pain_severity_score,
        'pain_interference_score': assessment.pain_interference_score,
    })


@login_required(login_url='health:login')
def corq_view(request):
    """CORQ assessment form and history."""
    assessments = CORQAssessment.objects.all()[:10]
    latest = assessments.first() if assessments else None

    context = {
        'assessments': assessments,
        'latest': latest,
    }
    return render(request, 'health/corq.html', context)


@login_required(login_url='health:login')
@require_POST
def save_corq(request):
    """Save CORQ assessment."""
    data = json.loads(request.body)
    today = date.today()

    assessment = CORQAssessment.objects.create(
        user=request.user,
        date=today,
        energy_level=data['energy_level'],
        playfulness=data['playfulness'],
        interest_in_surroundings=data['interest_in_surroundings'],
        appetite=data['appetite'],
        seeks_attention=data['seeks_attention'],
        enjoys_interaction=data['enjoys_interaction'],
        greets_family=data['greets_family'],
        tail_wagging=data['tail_wagging'],
        shows_pain=data['shows_pain'],
        vocalizes_pain=data['vocalizes_pain'],
        avoids_touch=data['avoids_touch'],
        pants_restless=data['pants_restless'],
        walks_normally=data['walks_normally'],
        rises_easily=data['rises_easily'],
        climbs_stairs=data['climbs_stairs'],
        jumps=data['jumps'],
        global_qol=data['global_qol'],
        notes=data.get('notes', '')
    )

    return JsonResponse({
        'status': 'success',
        'total_score': assessment.total_score,
        'vitality_score': assessment.vitality_score,
        'companionship_score': assessment.companionship_score,
        'pain_score': assessment.pain_score,
        'mobility_score': assessment.mobility_score,
    })


@login_required(login_url='health:login')
def treatments_view(request):
    """Treatment sessions history."""
    treatments = TreatmentSession.objects.all()[:20]

    context = {
        'treatments': treatments,
    }
    return render(request, 'health/treatments.html', context)


@login_required(login_url='health:login')
@require_POST
def save_treatment(request):
    """Save treatment session."""
    data = json.loads(request.body)

    treatment = TreatmentSession.objects.create(
        user=request.user,
        date=data.get('date', date.today()),
        treatment_type=data['treatment_type'],
        protocol=data.get('protocol', ''),
        agent=data.get('agent', ''),
        dose=data.get('dose', ''),
        cycle_number=data.get('cycle_number'),
        pre_treatment_weight=data.get('pre_treatment_weight'),
        notes=data.get('notes', '')
    )

    return JsonResponse({'status': 'success', 'id': treatment.id})


@login_required(login_url='health:login')
def events_view(request):
    """Adverse events (VCOG-CTCAE) tracking."""
    events = VCOGCTCAEEvent.objects.all()[:20]
    unresolved = VCOGCTCAEEvent.objects.filter(resolved=False)

    context = {
        'events': events,
        'unresolved': unresolved,
    }
    return render(request, 'health/events.html', context)


@login_required(login_url='health:login')
@require_POST
def save_event(request):
    """Save adverse event."""
    data = json.loads(request.body)

    event = VCOGCTCAEEvent.objects.create(
        user=request.user,
        date=data.get('date', date.today()),
        category=data['category'],
        event=data['event'],
        grade=data['grade'],
        treatment=data.get('treatment', ''),
        intervention=data.get('intervention', ''),
        notes=data.get('notes', '')
    )

    return JsonResponse({'status': 'success', 'id': event.id})


def set_language(request):
    """Set user's preferred language."""
    if request.method == 'POST':
        lang = request.POST.get('language', 'en')
        if lang in [code for code, _ in settings.LANGUAGES]:
            request.session['django_language'] = lang
    return redirect(request.META.get('HTTP_REFERER', '/health/'))


# ==================== NUTRITION TRACKING ====================

@login_required(login_url='health:login')
def nutrition_view(request):
    """
    Main nutrition tracking page.

    Shows daily meal logging, supplement tracking, and nutritional targets
    based on dog's weight and zero-carbohydrate cancer diet protocol.

    Scientific basis:
    - Ogilvie GK et al. Cancer. 2000;88(8):1916-1928.
    - Vail DM, Ogilvie GK et al. J Vet Intern Med. 1990;4(1):8-14.
    """
    today = date.today()

    # Get or create dog profile
    profile, created = DogProfile.objects.get_or_create(
        user=request.user,
        defaults={'name': 'Bruno', 'weight_kg': 22}
    )

    # Today's meals
    meals = Meal.objects.filter(user=request.user, date=today)

    # Today's supplements
    supplements = SupplementDose.objects.filter(user=request.user, date=today)

    # Calculate today's totals
    total_food_g = sum(m.total_grams for m in meals)
    total_protein_g = sum(m.total_protein_g for m in meals)
    total_fat_g = sum(m.total_fat_g for m in meals)
    total_carbs_g = sum(m.total_carbs_g for m in meals)

    # Supplement totals
    calcium_supplements = supplements.filter(supplement_type='calcium')
    fish_oil_supplements = supplements.filter(supplement_type='fish_oil')
    total_calcium_mg = sum(s.calcium_mg or 0 for s in calcium_supplements)
    total_omega3_mg = sum(s.omega3_total_mg for s in fish_oil_supplements)
    multivitamin_given = supplements.filter(supplement_type='multivitamin').exists()

    # Get approved foods for the form
    approved_foods = Food.objects.filter(status__in=['approved', 'limited']).order_by('category', 'name')

    # Warnings
    warnings = []
    if total_carbs_g > 5:
        warnings.append(_('Carbohydrate intake detected! Zero-carb target exceeded.'))
    if total_calcium_mg < profile.daily_calcium_min_mg * 0.5:
        warnings.append(_('Calcium supplementation below target.'))
    if total_omega3_mg < profile.daily_omega3_min_mg * 0.5:
        warnings.append(_('Omega-3 (EPA/DHA) supplementation below target.'))
    if not multivitamin_given:
        warnings.append(_('Daily multivitamin not logged yet.'))

    context = {
        'profile': profile,
        'meals': meals,
        'supplements': supplements,
        'approved_foods': approved_foods,
        'today': today,
        # Totals
        'total_food_g': total_food_g,
        'total_protein_g': total_protein_g,
        'total_fat_g': total_fat_g,
        'total_carbs_g': total_carbs_g,
        'total_calcium_mg': total_calcium_mg,
        'total_omega3_mg': total_omega3_mg,
        'multivitamin_given': multivitamin_given,
        # Targets
        'food_target_min': profile.daily_food_min_g,
        'food_target_max': profile.daily_food_max_g,
        'calcium_target_min': profile.daily_calcium_min_mg,
        'calcium_target_max': profile.daily_calcium_max_mg,
        'omega3_target_min': profile.daily_omega3_min_mg,
        'omega3_target_max': profile.daily_omega3_max_mg,
        # Warnings
        'warnings': warnings,
    }
    return render(request, 'health/nutrition.html', context)


@login_required(login_url='health:login')
@require_POST
def save_meal(request):
    """Save a meal with items."""
    data = json.loads(request.body)

    meal = Meal.objects.create(
        user=request.user,
        date=data.get('date', date.today()),
        meal_type=data['meal_type'],
        time=data.get('time'),
        appetite=data.get('appetite', ''),
        hand_fed=data.get('hand_fed', False),
        warmed=data.get('warmed', False),
        notes=data.get('notes', '')
    )

    # Add meal items
    items = data.get('items', [])
    for item in items:
        food_id = item.get('food_id')
        food = Food.objects.get(pk=food_id) if food_id else None

        MealItem.objects.create(
            meal=meal,
            food=food,
            custom_food_name=item.get('custom_food_name', ''),
            amount_g=item['amount_g'],
            amount_display=item.get('amount_display', '')
        )

        # Check for blocked foods
        if food and food.status == 'blocked':
            return JsonResponse({
                'status': 'warning',
                'message': f'{food.name}: {food.warning}',
                'id': meal.id
            })

    return JsonResponse({
        'status': 'success',
        'id': meal.id,
        'total_grams': meal.total_grams,
        'total_protein_g': meal.total_protein_g,
        'total_fat_g': meal.total_fat_g,
        'total_carbs_g': meal.total_carbs_g,
    })


@login_required(login_url='health:login')
@require_POST
def save_supplement(request):
    """Save a supplement dose."""
    data = json.loads(request.body)

    supplement = SupplementDose.objects.create(
        user=request.user,
        date=data.get('date', date.today()),
        supplement_type=data['supplement_type'],
        product_name=data.get('product_name', ''),
        dose_amount=data.get('dose_amount', ''),
        calcium_mg=data.get('calcium_mg'),
        epa_mg=data.get('epa_mg'),
        dha_mg=data.get('dha_mg'),
        notes=data.get('notes', '')
    )

    return JsonResponse({
        'status': 'success',
        'id': supplement.id,
        'omega3_total': supplement.omega3_total_mg
    })


@login_required(login_url='health:login')
@require_POST
def update_weight(request):
    """Update dog's weight."""
    data = json.loads(request.body)

    profile, created = DogProfile.objects.get_or_create(
        user=request.user,
        defaults={'name': 'Bruno', 'weight_kg': data['weight_kg']}
    )

    if not created:
        profile.weight_kg = data['weight_kg']
        if 'target_weight_kg' in data:
            profile.target_weight_kg = data['target_weight_kg']
        profile.save()

    return JsonResponse({
        'status': 'success',
        'weight_kg': float(profile.weight_kg),
        'daily_food_min_g': profile.daily_food_min_g,
        'daily_food_max_g': profile.daily_food_max_g,
        'daily_calcium_min_mg': profile.daily_calcium_min_mg,
        'daily_calcium_max_mg': profile.daily_calcium_max_mg,
        'daily_omega3_min_mg': profile.daily_omega3_min_mg,
        'daily_omega3_max_mg': profile.daily_omega3_max_mg,
    })


@login_required(login_url='health:login')
def food_database(request):
    """View food database with status indicators."""
    foods = Food.objects.all().order_by('status', 'category', 'name')

    context = {
        'foods': foods,
        'categories': Food.CATEGORY_CHOICES,
        'statuses': Food.STATUS_CHOICES,
    }
    return render(request, 'health/food_database.html', context)


@login_required(login_url='health:login')
def api_foods(request):
    """API endpoint for food database."""
    category = request.GET.get('category')
    status = request.GET.get('status')

    foods = Food.objects.all()
    if category:
        foods = foods.filter(category=category)
    if status:
        foods = foods.filter(status=status)

    data = [{
        'id': f.id,
        'name': f.name,
        'category': f.category,
        'status': f.status,
        'calories_per_100g': f.calories_per_100g,
        'protein_g_per_100g': float(f.protein_g_per_100g) if f.protein_g_per_100g else None,
        'fat_g_per_100g': float(f.fat_g_per_100g) if f.fat_g_per_100g else None,
        'carbs_g_per_100g': float(f.carbs_g_per_100g) if f.carbs_g_per_100g else None,
        'warning': f.warning,
        'notes': f.notes,
    } for f in foods]

    return JsonResponse({'foods': data})


@login_required(login_url='health:login')
def api_nutrition_summary(request):
    """API endpoint for nutrition summary over time."""
    days = int(request.GET.get('days', 7))
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    # Get meals for the period
    meals_by_date = {}
    meals = Meal.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    for meal in meals:
        d = meal.date.isoformat()
        if d not in meals_by_date:
            meals_by_date[d] = {
                'food_g': 0,
                'protein_g': 0,
                'fat_g': 0,
                'carbs_g': 0,
            }
        meals_by_date[d]['food_g'] += meal.total_grams
        meals_by_date[d]['protein_g'] += meal.total_protein_g
        meals_by_date[d]['fat_g'] += meal.total_fat_g
        meals_by_date[d]['carbs_g'] += meal.total_carbs_g

    # Build response
    labels = []
    food_data = []
    protein_data = []
    fat_data = []
    carbs_data = []

    current = start_date
    while current <= end_date:
        d = current.isoformat()
        labels.append(current.strftime('%m/%d'))
        if d in meals_by_date:
            food_data.append(meals_by_date[d]['food_g'])
            protein_data.append(meals_by_date[d]['protein_g'])
            fat_data.append(meals_by_date[d]['fat_g'])
            carbs_data.append(meals_by_date[d]['carbs_g'])
        else:
            food_data.append(0)
            protein_data.append(0)
            fat_data.append(0)
            carbs_data.append(0)
        current += timedelta(days=1)

    return JsonResponse({
        'labels': labels,
        'food_g': food_data,
        'protein_g': protein_data,
        'fat_g': fat_data,
        'carbs_g': carbs_data,
    })


@login_required(login_url='health:login')
def meal_planning_view(request):
    """
    Comprehensive meal planning guide for homemade cancer diet.

    Includes:
    - Sample weekly meal plans
    - Food preparation instructions
    - Supplement preparation guides
    - Shopping lists
    - Portion calculators based on weight
    """
    # Get or create dog profile
    profile, created = DogProfile.objects.get_or_create(
        user=request.user,
        defaults={'name': 'Bruno', 'weight_kg': 22}
    )

    # Calculate daily food targets
    weight_kg = float(profile.weight_kg)
    daily_food_min = weight_kg * 1000 * 0.025  # 2.5% body weight
    daily_food_max = weight_kg * 1000 * 0.030  # 3.0% body weight
    daily_food_target = (daily_food_min + daily_food_max) / 2

    # Meal portions (assuming 3 meals/day)
    meal_portion = daily_food_target / 3

    # Macronutrient targets (grams per day)
    # High protein: 30-45% of calories from protein
    # High fat: 30-50% of calories from fat
    # Zero carbs

    # Sample meal plans with portion sizes based on weight
    sample_meals = {
        'breakfast': [
            {
                'name': _('Scrambled Eggs + Chicken'),
                'items': [
                    {'food': 'Eggs (scrambled)', 'amount': round(meal_portion * 0.3)},
                    {'food': 'Chicken breast (boiled)', 'amount': round(meal_portion * 0.7)},
                ],
                'prep_time': '10 min',
                'notes': _('Scramble eggs without oil. Chop pre-cooked chicken.')
            },
            {
                'name': _('Sardine Bowl'),
                'items': [
                    {'food': 'Sardines (canned in water)', 'amount': round(meal_portion * 0.5)},
                    {'food': 'Hard-boiled egg', 'amount': round(meal_portion * 0.3)},
                    {'food': 'Chicken broth', 'amount': round(meal_portion * 0.2)},
                ],
                'prep_time': '5 min',
                'notes': _('Mash sardines, chop egg, mix with warm broth.')
            },
        ],
        'lunch': [
            {
                'name': _('Ground Beef Mix'),
                'items': [
                    {'food': 'Ground beef (cooked)', 'amount': round(meal_portion * 0.8)},
                    {'food': 'Chicken liver (cooked)', 'amount': round(meal_portion * 0.2)},
                ],
                'prep_time': '15 min',
                'notes': _('Pan-cook beef until no pink. Add small amount of liver for nutrients.')
            },
            {
                'name': _('Turkey & Egg'),
                'items': [
                    {'food': 'Turkey (ground, cooked)', 'amount': round(meal_portion * 0.7)},
                    {'food': 'Egg (scrambled)', 'amount': round(meal_portion * 0.3)},
                ],
                'prep_time': '12 min',
                'notes': _('Cook turkey thoroughly. Mix with scrambled egg.')
            },
        ],
        'dinner': [
            {
                'name': _('Salmon Dinner'),
                'items': [
                    {'food': 'Salmon (baked/canned)', 'amount': round(meal_portion * 0.6)},
                    {'food': 'Chicken thigh (boiled)', 'amount': round(meal_portion * 0.4)},
                ],
                'prep_time': '20 min',
                'notes': _('Excellent omega-3 source. Remove skin if watching fat.')
            },
            {
                'name': _('Lamb & Chicken'),
                'items': [
                    {'food': 'Lamb (ground, cooked)', 'amount': round(meal_portion * 0.5)},
                    {'food': 'Chicken breast (boiled)', 'amount': round(meal_portion * 0.5)},
                ],
                'prep_time': '15 min',
                'notes': _('Higher fat option good for maintaining weight.')
            },
        ],
    }

    # Weekly shopping list based on 7-day plan
    weekly_protein_g = daily_food_target * 7
    shopping_list = [
        {'item': _('Chicken breast/thigh'), 'amount': f'{round(weekly_protein_g * 0.3 / 1000, 1)} kg'},
        {'item': _('Ground beef (lean)'), 'amount': f'{round(weekly_protein_g * 0.25 / 1000, 1)} kg'},
        {'item': _('Eggs'), 'amount': f'{min(21, round(weekly_protein_g * 0.15 / 50))} units'},  # Max 3/day
        {'item': _('Sardines (canned)'), 'amount': f'{round(weekly_protein_g * 0.1 / 100)} cans'},
        {'item': _('Salmon (fresh or canned)'), 'amount': f'{round(weekly_protein_g * 0.1 / 1000, 1)} kg'},
        {'item': _('Turkey (ground)'), 'amount': f'{round(weekly_protein_g * 0.1 / 1000, 1)} kg'},
    ]

    # Supplement needs
    calcium_daily = weight_kg * 55  # 50-60mg per kg
    omega3_daily = weight_kg * 75   # 50-100mg per kg

    context = {
        'profile': profile,
        'daily_food_min': daily_food_min,
        'daily_food_max': daily_food_max,
        'daily_food_target': daily_food_target,
        'meal_portion': meal_portion,
        'sample_meals': sample_meals,
        'shopping_list': shopping_list,
        'calcium_daily': calcium_daily,
        'omega3_daily': omega3_daily,
    }
    return render(request, 'health/meal_planning.html', context)


# ==================== MEDICAL RECORDS ====================

@login_required(login_url='health:login')
def records_view(request):
    """
    Medical records gallery and upload.

    Allows users to upload and view blood work, cytology reports,
    and other medical documents. Records can be parsed by AI to
    extract lab values automatically.
    """
    records = MedicalRecord.objects.filter(user=request.user).order_by('-date')

    # Get recent lab values with trends
    recent_lab_values = LabValue.objects.filter(user=request.user).order_by('-date')[:50]

    # Group lab values by test name for trend display
    lab_trends = {}
    for lv in recent_lab_values:
        test_name = lv.get_test_name_display()
        if test_name not in lab_trends:
            lab_trends[test_name] = []
        lab_trends[test_name].append({
            'date': lv.date,
            'value': float(lv.value),
            'unit': lv.unit,
            'is_abnormal': lv.is_abnormal,
            'is_critical': lv.is_critical,
        })

    # Check if AI parsing is enabled
    settings = SiteSettings.get_settings()
    ai_enabled = settings.enable_ai_parsing and (settings.claude_api_key or settings.openai_api_key)

    context = {
        'records': records,
        'lab_trends': lab_trends,
        'ai_enabled': ai_enabled,
        'record_types': MedicalRecord.RECORD_TYPE_CHOICES,
    }
    return render(request, 'health/records.html', context)


@login_required(login_url='health:login')
@require_POST
def upload_record(request):
    """Upload a medical record file."""
    record_type = request.POST.get('record_type')
    record_date = request.POST.get('date', date.today())
    title = request.POST.get('title', '')
    clinic_name = request.POST.get('clinic_name', '')
    veterinarian = request.POST.get('veterinarian', '')
    source = request.POST.get('source', 'clinic')
    notes = request.POST.get('notes', '')
    uploaded_file = request.FILES.get('file')

    if not uploaded_file:
        return JsonResponse({'status': 'error', 'message': 'No file uploaded'}, status=400)

    record = MedicalRecord.objects.create(
        user=request.user,
        date=record_date,
        record_type=record_type,
        title=title,
        file=uploaded_file,
        source=source,
        clinic_name=clinic_name,
        veterinarian=veterinarian,
        notes=notes,
    )

    return JsonResponse({
        'status': 'success',
        'id': record.id,
        'message': _('Record uploaded successfully'),
    })


@login_required(login_url='health:login')
def record_detail(request, record_id):
    """View a single medical record with its lab values."""
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)
    lab_values = record.lab_values.all().order_by('test_name')

    context = {
        'record': record,
        'lab_values': lab_values,
        'record_types': MedicalRecord.RECORD_TYPE_CHOICES,
    }
    return render(request, 'health/record_detail.html', context)


@login_required(login_url='health:login')
def edit_record(request, record_id):
    """Edit a medical record."""
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)

    if request.method == 'POST':
        record.record_type = request.POST.get('record_type', record.record_type)
        record.title = request.POST.get('title', record.title)
        record.date = request.POST.get('date', record.date)
        record.source = request.POST.get('source', record.source)
        record.clinic_name = request.POST.get('clinic_name', record.clinic_name)
        record.veterinarian = request.POST.get('veterinarian', record.veterinarian)
        record.notes = request.POST.get('notes', record.notes)

        # Handle file replacement if new file uploaded
        if request.FILES.get('file'):
            record.file = request.FILES['file']

        record.save()
        return redirect('health:record_detail', record_id=record.id)

    context = {
        'record': record,
        'record_types': MedicalRecord.RECORD_TYPE_CHOICES,
    }
    return render(request, 'health/record_edit.html', context)


@login_required(login_url='health:login')
@require_POST
def delete_record(request, record_id):
    """Delete a medical record."""
    record = get_object_or_404(MedicalRecord, id=record_id, user=request.user)

    # Delete the file from storage
    if record.file:
        record.file.delete(save=False)

    record.delete()

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success'})

    return redirect('health:records')


@login_required(login_url='health:login')
def api_lab_values(request):
    """API endpoint for lab value trends over time."""
    test_name = request.GET.get('test')
    days = int(request.GET.get('days', 365))
    end_date = date.today()
    start_date = end_date - timedelta(days=days)

    lab_values = LabValue.objects.filter(
        user=request.user,
        date__gte=start_date,
        date__lte=end_date
    ).order_by('date')

    if test_name:
        lab_values = lab_values.filter(test_name=test_name)

    # Group by test type
    data = {}
    for lv in lab_values:
        test = lv.test_name
        if test not in data:
            data[test] = {
                'labels': [],
                'values': [],
                'reference_low': None,
                'reference_high': None,
                'unit': lv.unit,
            }
        data[test]['labels'].append(lv.date.strftime('%Y-%m-%d'))
        data[test]['values'].append(float(lv.value))
        if lv.reference_low and not data[test]['reference_low']:
            data[test]['reference_low'] = float(lv.reference_low)
        if lv.reference_high and not data[test]['reference_high']:
            data[test]['reference_high'] = float(lv.reference_high)

    return JsonResponse(data)
