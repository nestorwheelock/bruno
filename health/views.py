from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import date, timedelta
import json

from .models import DailyEntry, Medication, MedicationDose, LymphNodeMeasurement


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
