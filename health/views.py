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
    CBPIAssessment, CORQAssessment, VCOGCTCAEEvent, TreatmentSession
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
    entry, created = DailyEntry.objects.get_or_create(
        date=today,
        defaults={'user': request.user}
    )
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

    # Get latest assessments
    latest_cbpi = CBPIAssessment.objects.first()
    latest_corq = CORQAssessment.objects.first()
    latest_node = LymphNodeMeasurement.objects.first()

    # Recent adverse events
    recent_events = VCOGCTCAEEvent.objects.filter(
        date__gte=thirty_days_ago, resolved=False
    ).order_by('-grade', '-date')[:5]

    # Recent treatments
    recent_treatments = TreatmentSession.objects.filter(
        date__gte=thirty_days_ago
    )[:5]

    # Daily entry stats
    entries = DailyEntry.objects.filter(date__gte=thirty_days_ago)
    good_days = entries.filter(good_day='yes').count()
    mixed_days = entries.filter(good_day='mixed').count()
    bad_days = entries.filter(good_day='no').count()
    total_days = good_days + mixed_days + bad_days

    # Calculate QoL status color based on CORQ
    qol_status = 'gray'
    qol_message = _('No assessments yet')
    if latest_corq:
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
        'latest_cbpi': latest_cbpi,
        'latest_corq': latest_corq,
        'latest_node': latest_node,
        'recent_events': recent_events,
        'recent_treatments': recent_treatments,
        'good_days': good_days,
        'mixed_days': mixed_days,
        'bad_days': bad_days,
        'total_days': total_days,
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
