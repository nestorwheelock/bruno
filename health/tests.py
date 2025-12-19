from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import (
    DailyEntry, Medication, MedicationDose, LymphNodeMeasurement,
    Provider, TimelineEntry, TimelineAttachment,
    CBPIAssessment, CORQAssessment, TreatmentSession, VCOGCTCAEEvent,
    DogProfile, Meal, MealItem, Food, SupplementDose, MedicalRecord, LabValue
)
from datetime import time


class DailyEntryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_daily_entry(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes'
        )
        self.assertEqual(entry.good_day, 'yes')
        self.assertEqual(entry.user, self.user)

    def test_daily_entry_str(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date(2024, 1, 15)
        )
        self.assertEqual(str(entry), "Entry for 2024-01-15")

    def test_daily_entry_ordering(self):
        entry1 = DailyEntry.objects.create(
            user=self.user, date=date(2024, 1, 10)
        )
        entry2 = DailyEntry.objects.create(
            user=self.user, date=date(2024, 1, 15)
        )
        entries = list(DailyEntry.objects.all())
        self.assertEqual(entries[0], entry2)
        self.assertEqual(entries[1], entry1)

    def test_daily_entry_unique_date(self):
        DailyEntry.objects.create(user=self.user, date=date.today())
        with self.assertRaises(Exception):
            DailyEntry.objects.create(user=self.user, date=date.today())

    def test_happiness_score_with_values(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            tail_body_language=4,
            interest_people=3,
            interest_environment=5,
            enjoyment_favorites=4,
            overall_spark=4
        )
        self.assertEqual(entry.happiness_score, 4.0)

    def test_happiness_score_partial_values(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            tail_body_language=3,
            interest_people=5
        )
        self.assertEqual(entry.happiness_score, 4.0)

    def test_happiness_score_no_values(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today()
        )
        self.assertIsNone(entry.happiness_score)

    def test_overall_score_with_values(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            tail_body_language=4,
            interest_people=4,
            interest_environment=4,
            enjoyment_favorites=4,
            overall_spark=4,
            appetite=4,
            food_enjoyment=4,
            nausea_signs=4,
            weight_condition=4,
            energy_level=4,
            willingness_move=4,
            walking_comfort=4,
            resting_comfort=4,
            breathing_comfort=4,
            pain_signs=4,
            sleep_quality=4,
            response_touch=4
        )
        self.assertEqual(entry.overall_score, 4.0)

    def test_overall_score_no_values(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today()
        )
        self.assertIsNone(entry.overall_score)

    def test_good_day_choices(self):
        for choice in ['yes', 'mixed', 'no']:
            entry = DailyEntry.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=hash(choice) % 100 + 1)
            )
            entry.good_day = choice
            entry.save()
            self.assertEqual(entry.good_day, choice)

    def test_meal_tracking_booleans(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            breakfast=True,
            lunch=True,
            dinner=False,
            treats=True
        )
        self.assertTrue(entry.breakfast)
        self.assertTrue(entry.lunch)
        self.assertFalse(entry.dinner)
        self.assertTrue(entry.treats)

    def test_notes_fields(self):
        entry = DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_notes="Played fetch",
            hard_notes="Didn't want to eat",
            other_notes="Vet visit tomorrow"
        )
        self.assertEqual(entry.good_notes, "Played fetch")
        self.assertEqual(entry.hard_notes, "Didn't want to eat")
        self.assertEqual(entry.other_notes, "Vet visit tomorrow")


class MedicationModelTests(TestCase):
    def test_create_medication(self):
        med = Medication.objects.create(
            name='Prednisone',
            dosage='5mg',
            frequency='twice'
        )
        self.assertEqual(med.name, 'Prednisone')
        self.assertEqual(med.dosage, '5mg')
        self.assertTrue(med.active)

    def test_medication_str(self):
        med = Medication.objects.create(
            name='Prednisone',
            dosage='5mg',
            frequency='once'
        )
        self.assertEqual(str(med), "Prednisone (5mg)")

    def test_medication_frequency_choices(self):
        for freq in ['once', 'twice', 'three', 'asNeeded']:
            med = Medication.objects.create(
                name=f'Med_{freq}',
                dosage='10mg',
                frequency=freq
            )
            self.assertEqual(med.frequency, freq)

    def test_medication_with_notes(self):
        med = Medication.objects.create(
            name='Ondansetron',
            dosage='4mg',
            frequency='asNeeded',
            notes='Give 30 min before chemo'
        )
        self.assertEqual(med.notes, 'Give 30 min before chemo')

    def test_medication_inactive(self):
        med = Medication.objects.create(
            name='Old Med',
            dosage='1mg',
            frequency='once',
            active=False
        )
        self.assertFalse(med.active)


class MedicationDoseModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.medication = Medication.objects.create(
            name='Prednisone',
            dosage='5mg',
            frequency='twice'
        )

    def test_create_dose(self):
        dose = MedicationDose.objects.create(
            medication=self.medication,
            user=self.user,
            given_at=timezone.now()
        )
        self.assertEqual(dose.medication, self.medication)
        self.assertEqual(dose.user, self.user)

    def test_dose_str(self):
        given_time = timezone.now()
        dose = MedicationDose.objects.create(
            medication=self.medication,
            user=self.user,
            given_at=given_time
        )
        self.assertIn('Prednisone', str(dose))

    def test_dose_ordering(self):
        dose1 = MedicationDose.objects.create(
            medication=self.medication,
            user=self.user,
            given_at=timezone.now() - timedelta(hours=2)
        )
        dose2 = MedicationDose.objects.create(
            medication=self.medication,
            user=self.user,
            given_at=timezone.now()
        )
        doses = list(MedicationDose.objects.all())
        self.assertEqual(doses[0], dose2)
        self.assertEqual(doses[1], dose1)

    def test_dose_with_notes(self):
        dose = MedicationDose.objects.create(
            medication=self.medication,
            user=self.user,
            given_at=timezone.now(),
            notes='Given with food'
        )
        self.assertEqual(dose.notes, 'Given with food')

    def test_dose_related_name(self):
        MedicationDose.objects.create(
            medication=self.medication,
            user=self.user,
            given_at=timezone.now()
        )
        self.assertEqual(self.medication.doses.count(), 1)


class LymphNodeMeasurementModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_create_measurement(self):
        measurement = LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date.today(),
            mandibular_left=Decimal('2.5'),
            mandibular_right=Decimal('2.3')
        )
        self.assertEqual(measurement.mandibular_left, Decimal('2.5'))
        self.assertEqual(measurement.mandibular_right, Decimal('2.3'))

    def test_measurement_str(self):
        measurement = LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date(2024, 1, 15)
        )
        self.assertEqual(str(measurement), "Node measurement on 2024-01-15")

    def test_measurement_ordering(self):
        m1 = LymphNodeMeasurement.objects.create(
            user=self.user, date=date(2024, 1, 10)
        )
        m2 = LymphNodeMeasurement.objects.create(
            user=self.user, date=date(2024, 1, 15)
        )
        measurements = list(LymphNodeMeasurement.objects.all())
        self.assertEqual(measurements[0], m2)
        self.assertEqual(measurements[1], m1)

    def test_measurement_status_choices(self):
        for status in ['smaller', 'same', 'larger']:
            m = LymphNodeMeasurement.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=hash(status) % 100 + 1),
                status=status
            )
            self.assertEqual(m.status, status)

    def test_measurement_all_nodes(self):
        measurement = LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date.today(),
            mandibular_left=Decimal('2.5'),
            mandibular_right=Decimal('2.3'),
            popliteal_left=Decimal('1.8'),
            popliteal_right=Decimal('1.7'),
            status='same',
            notes='Stable'
        )
        self.assertEqual(measurement.popliteal_left, Decimal('1.8'))
        self.assertEqual(measurement.popliteal_right, Decimal('1.7'))
        self.assertEqual(measurement.notes, 'Stable')


class LoginViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.login_url = reverse('health:login')

    def test_login_page_get(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/login.html')

    def test_login_success(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('health:tracker'))

    def test_login_invalid_credentials(self):
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')

    def test_login_redirect_if_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('health:tracker'))


class LogoutViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('health:logout'))
        self.assertRedirects(response, reverse('health:login'))


class TrackerViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.tracker_url = reverse('health:tracker')

    def test_tracker_requires_login(self):
        response = self.client.get(self.tracker_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.tracker_url}")

    def test_tracker_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.tracker_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/tracker.html')

    def test_tracker_creates_entry(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.get(self.tracker_url)
        self.assertTrue(DailyEntry.objects.filter(date=date.today()).exists())

    def test_tracker_context(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.tracker_url)
        self.assertIn('entry', response.context)
        self.assertIn('medications', response.context)
        self.assertIn('today_doses', response.context)
        self.assertIn('good_day_percent', response.context)


class SaveDailyEntryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_entry')

    def test_save_requires_login(self):
        response = self.client.post(self.save_url)
        self.assertEqual(response.status_code, 302)

    def test_save_requires_post(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.save_url)
        self.assertEqual(response.status_code, 405)

    def test_save_daily_entry(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'good_day': 'yes',
            'tail_body_language': 4,
            'interest_people': 5,
            'appetite': 3,
            'breakfast': True,
            'good_notes': 'Great day!'
        }
        response = self.client.post(
            self.save_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')

        entry = DailyEntry.objects.get(date=date.today())
        self.assertEqual(entry.good_day, 'yes')
        self.assertEqual(entry.tail_body_language, 4)
        self.assertTrue(entry.breakfast)

    def test_save_updates_existing_entry(self):
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(user=self.user, date=date.today(), good_day='no')

        data = {'good_day': 'yes'}
        self.client.post(
            self.save_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(DailyEntry.objects.filter(date=date.today()).count(), 1)
        entry = DailyEntry.objects.get(date=date.today())
        self.assertEqual(entry.good_day, 'yes')


class AddMedicationViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.add_url = reverse('health:add_medication')

    def test_add_requires_login(self):
        response = self.client.post(self.add_url)
        self.assertEqual(response.status_code, 302)

    def test_add_medication(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'Prednisone',
            'dosage': '5mg',
            'frequency': 'twice',
            'notes': 'With food'
        }
        response = self.client.post(
            self.add_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertEqual(result['name'], 'Prednisone')

        self.assertTrue(Medication.objects.filter(name='Prednisone').exists())


class RecordDoseViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.medication = Medication.objects.create(
            name='Prednisone',
            dosage='5mg',
            frequency='twice'
        )
        self.record_url = reverse('health:record_dose', args=[self.medication.id])

    def test_record_requires_login(self):
        response = self.client.post(self.record_url)
        self.assertEqual(response.status_code, 302)

    def test_record_dose(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.record_url)
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')
        self.assertIn('time', result)

        self.assertEqual(MedicationDose.objects.count(), 1)

    def test_record_dose_invalid_medication(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(reverse('health:record_dose', args=[9999]))
        self.assertEqual(response.status_code, 404)


class SaveNodeMeasurementViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_nodes')

    def test_save_requires_login(self):
        response = self.client.post(self.save_url)
        self.assertEqual(response.status_code, 302)

    def test_save_node_measurement(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'mandibular_left': '2.5',
            'mandibular_right': '2.3',
            'popliteal_left': '1.8',
            'popliteal_right': '1.7',
            'status': 'same',
            'notes': 'Stable'
        }
        response = self.client.post(
            self.save_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = json.loads(response.content)
        self.assertEqual(result['status'], 'success')

        measurement = LymphNodeMeasurement.objects.get(date=date.today())
        self.assertEqual(measurement.mandibular_left, Decimal('2.5'))
        self.assertEqual(measurement.status, 'same')

    def test_save_updates_existing_measurement(self):
        self.client.login(username='testuser', password='testpass123')
        LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date.today(),
            status='smaller'
        )

        data = {'status': 'larger'}
        self.client.post(
            self.save_url,
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(LymphNodeMeasurement.objects.filter(date=date.today()).count(), 1)
        measurement = LymphNodeMeasurement.objects.get(date=date.today())
        self.assertEqual(measurement.status, 'larger')


class HistoryViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.history_url = reverse('health:history')

    def test_history_requires_login(self):
        response = self.client.get(self.history_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.history_url}")

    def test_history_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/history.html')

    def test_history_context(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.history_url)
        self.assertIn('entries', response.context)
        self.assertIn('node_measurements', response.context)
        self.assertIn('good_day_percent', response.context)
        self.assertIn('trend', response.context)

    def test_history_trend_calculation(self):
        self.client.login(username='testuser', password='testpass123')
        for i in range(7):
            DailyEntry.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=i),
                good_day='yes'
            )
        for i in range(7, 14):
            DailyEntry.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=i),
                good_day='no'
            )

        response = self.client.get(self.history_url)
        self.assertEqual(response.context['trend'], 'Better')


class MedicationsViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.medications_url = reverse('health:medications')

    def test_medications_requires_login(self):
        response = self.client.get(self.medications_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.medications_url}")

    def test_medications_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.medications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/medications.html')

    def test_medications_context(self):
        self.client.login(username='testuser', password='testpass123')
        Medication.objects.create(name='Test Med', dosage='5mg', frequency='once')
        response = self.client.get(self.medications_url)
        self.assertIn('medications', response.context)
        self.assertIn('today_doses', response.context)
        self.assertEqual(response.context['medications'].count(), 1)

    def test_medications_only_active(self):
        self.client.login(username='testuser', password='testpass123')
        Medication.objects.create(name='Active', dosage='5mg', frequency='once', active=True)
        Medication.objects.create(name='Inactive', dosage='5mg', frequency='once', active=False)
        response = self.client.get(self.medications_url)
        self.assertEqual(response.context['medications'].count(), 1)


class NodesViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.nodes_url = reverse('health:nodes')

    def test_nodes_requires_login(self):
        response = self.client.get(self.nodes_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.nodes_url}")

    def test_nodes_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.nodes_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/nodes.html')

    def test_nodes_context(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.nodes_url)
        self.assertIn('measurement', response.context)
        self.assertIn('history', response.context)

    def test_nodes_shows_today_measurement(self):
        self.client.login(username='testuser', password='testpass123')
        measurement = LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date.today(),
            mandibular_left=Decimal('2.5')
        )
        response = self.client.get(self.nodes_url)
        self.assertEqual(response.context['measurement'], measurement)


# ============================================================================
# Provider Model Tests
# ============================================================================

class ProviderModelTests(TestCase):
    def test_create_provider(self):
        provider = Provider.objects.create(
            name='Dr. Test',
            clinic_name='Test Clinic',
            location='Test City',
            trust_rating=4
        )
        self.assertEqual(provider.name, 'Dr. Test')
        self.assertEqual(provider.trust_rating, 4)

    def test_provider_str(self):
        provider = Provider.objects.create(
            name='Dr. Pablo',
            clinic_name='Vet Friendly'
        )
        self.assertIn('Dr. Pablo', str(provider))

    def test_provider_trust_rating_choices(self):
        for rating in [1, 2, 3, 4, 5]:
            provider = Provider.objects.create(
                name=f'Provider_{rating}',
                trust_rating=rating
            )
            self.assertEqual(provider.trust_rating, rating)

    def test_provider_with_issues(self):
        provider = Provider.objects.create(
            name='Bad Vet',
            trust_rating=1,
            issues='Many problems documented'
        )
        self.assertEqual(provider.issues, 'Many problems documented')


# ============================================================================
# TimelineEntry Model Tests
# ============================================================================

class TimelineEntryModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.provider = Provider.objects.create(
            name='Dr. Test',
            trust_rating=5
        )

    def test_create_timeline_entry(self):
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Test Visit',
            content='Test content'
        )
        self.assertEqual(entry.title, 'Test Visit')
        self.assertEqual(entry.entry_type, 'vet_visit')

    def test_timeline_entry_str(self):
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=date(2024, 12, 15),
            entry_type='symptom',
            title='Test Entry'
        )
        self.assertIn('Test Entry', str(entry))

    def test_timeline_entry_with_provider(self):
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Vet Visit',
            provider=self.provider
        )
        self.assertEqual(entry.provider.name, 'Dr. Test')

    def test_timeline_entry_ordering(self):
        entry1 = TimelineEntry.objects.create(
            user=self.user,
            date=date(2024, 12, 10),
            entry_type='symptom',
            title='Earlier Entry'
        )
        entry2 = TimelineEntry.objects.create(
            user=self.user,
            date=date(2024, 12, 15),
            entry_type='symptom',
            title='Later Entry'
        )
        entries = list(TimelineEntry.objects.filter(user=self.user).order_by('-date'))
        self.assertEqual(entries[0], entry2)
        self.assertEqual(entries[1], entry1)

    def test_timeline_entry_mood_choices(self):
        for mood in ['great', 'good', 'okay', 'poor', 'bad', 'unknown']:
            entry = TimelineEntry.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=hash(mood) % 100 + 1),
                entry_type='symptom',
                title=f'Mood test {mood}',
                bruno_mood=mood
            )
            self.assertEqual(entry.bruno_mood, mood)

    def test_timeline_entry_type_choices(self):
        entry_types = ['vet_visit', 'lab_result', 'imaging', 'procedure',
                       'treatment', 'medication', 'symptom', 'communication',
                       'milestone', 'concern', 'research', 'other']
        for i, entry_type in enumerate(entry_types):
            entry = TimelineEntry.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=i + 1),
                entry_type=entry_type,
                title=f'Type test {entry_type}'
            )
            self.assertEqual(entry.entry_type, entry_type)


class TimelineEntryStatusTests(TestCase):
    """Tests for timeline entry status field and auto-detection."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )

    def test_future_date_auto_scheduled(self):
        """Future dates should automatically be marked as scheduled."""
        future_date = date.today() + timedelta(days=7)
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=future_date,
            entry_type='vet_visit',
            title='Future Appointment'
        )
        self.assertEqual(entry.status, 'scheduled')

    def test_past_date_stays_completed(self):
        """Past dates should remain completed."""
        past_date = date.today() - timedelta(days=7)
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=past_date,
            entry_type='vet_visit',
            title='Past Visit'
        )
        self.assertEqual(entry.status, 'completed')

    def test_today_date_is_completed(self):
        """Today's date should be completed (not future)."""
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Today Visit'
        )
        self.assertEqual(entry.status, 'completed')

    def test_cancelled_status_preserved_future(self):
        """Cancelled status should not be auto-changed for future dates."""
        future_date = date.today() + timedelta(days=7)
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=future_date,
            entry_type='vet_visit',
            title='Cancelled Appointment',
            status='cancelled'
        )
        self.assertEqual(entry.status, 'cancelled')

    def test_cancelled_status_preserved_past(self):
        """Cancelled status should not be auto-changed for past dates."""
        past_date = date.today() - timedelta(days=7)
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=past_date,
            entry_type='vet_visit',
            title='Cancelled Past',
            status='cancelled'
        )
        self.assertEqual(entry.status, 'cancelled')

    def test_is_future_property_true(self):
        """Test is_future property returns True for future dates."""
        future_entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() + timedelta(days=1),
            entry_type='vet_visit',
            title='Future'
        )
        self.assertTrue(future_entry.is_future)

    def test_is_future_property_false(self):
        """Test is_future property returns False for past dates."""
        past_entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=1),
            entry_type='vet_visit',
            title='Past'
        )
        self.assertFalse(past_entry.is_future)

    def test_is_overdue_property(self):
        """Test is_overdue property for past scheduled entries."""
        past_date = date.today() - timedelta(days=1)
        # Create entry then force status to scheduled
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=past_date,
            entry_type='vet_visit',
            title='Overdue'
        )
        TimelineEntry.objects.filter(pk=entry.pk).update(status='scheduled')
        entry.refresh_from_db()
        self.assertTrue(entry.is_overdue)

    def test_is_overdue_false_for_completed(self):
        """Completed entries should not be overdue."""
        past_date = date.today() - timedelta(days=1)
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=past_date,
            entry_type='vet_visit',
            title='Completed Past',
            status='completed'
        )
        self.assertFalse(entry.is_overdue)

    def test_is_overdue_false_for_future(self):
        """Future scheduled entries should not be overdue."""
        future_entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() + timedelta(days=1),
            entry_type='vet_visit',
            title='Future Scheduled'
        )
        self.assertFalse(future_entry.is_overdue)

    def test_status_choices_valid(self):
        """Test all status choices are valid."""
        # Scheduled - use future date so it stays scheduled
        entry1 = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() + timedelta(days=10),
            entry_type='vet_visit',
            title='Status scheduled',
            status='scheduled'
        )
        self.assertEqual(entry1.status, 'scheduled')

        # Completed - use past date
        entry2 = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=10),
            entry_type='vet_visit',
            title='Status completed',
            status='completed'
        )
        self.assertEqual(entry2.status, 'completed')

        # Cancelled - use past date, should stay cancelled
        entry3 = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=10),
            entry_type='vet_visit',
            title='Status cancelled',
            status='cancelled'
        )
        self.assertEqual(entry3.status, 'cancelled')

    def test_default_status_is_completed(self):
        """Default status for past entries should be completed."""
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=5),
            entry_type='vet_visit',
            title='Default Status Test'
        )
        self.assertEqual(entry.status, 'completed')

    def test_status_update_on_save(self):
        """Updating date should update status appropriately."""
        # Create past entry
        entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today() - timedelta(days=5),
            entry_type='vet_visit',
            title='Changing Date'
        )
        self.assertEqual(entry.status, 'completed')

        # Change to future date
        entry.date = date.today() + timedelta(days=5)
        entry.save()
        self.assertEqual(entry.status, 'scheduled')


# ============================================================================
# Timeline View Tests
# ============================================================================

class TimelineViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.timeline_url = reverse('health:timeline')

    def test_timeline_requires_login(self):
        response = self.client.get(self.timeline_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.timeline_url}")

    def test_timeline_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.timeline_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/timeline.html')

    def test_timeline_context(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.timeline_url)
        self.assertIn('entries', response.context)
        self.assertIn('providers', response.context)
        self.assertIn('entry_types', response.context)

    def test_timeline_shows_entries(self):
        self.client.login(username='testuser', password='testpass123')
        TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Test Entry'
        )
        response = self.client.get(self.timeline_url)
        self.assertEqual(len(response.context['entries']), 1)


class TimelineDetailViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        # Create multiple entries for navigation testing
        self.entry1 = TimelineEntry.objects.create(
            user=self.user,
            date=date(2024, 12, 10),
            time=time(10, 0),
            entry_type='symptom',
            title='First Entry',
            content='First content'
        )
        self.entry2 = TimelineEntry.objects.create(
            user=self.user,
            date=date(2024, 12, 15),
            time=time(14, 0),
            entry_type='vet_visit',
            title='Second Entry',
            content='Second content'
        )
        self.entry3 = TimelineEntry.objects.create(
            user=self.user,
            date=date(2024, 12, 20),
            time=time(9, 0),
            entry_type='milestone',
            title='Third Entry',
            content='Third content'
        )

    def test_detail_requires_login(self):
        url = reverse('health:timeline_detail', args=[self.entry1.id])
        response = self.client.get(url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={url}")

    def test_detail_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('health:timeline_detail', args=[self.entry2.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/timeline_detail.html')

    def test_detail_context_has_entry(self):
        self.client.login(username='testuser', password='testpass123')
        url = reverse('health:timeline_detail', args=[self.entry2.id])
        response = self.client.get(url)
        self.assertEqual(response.context['entry'], self.entry2)

    def test_detail_has_prev_next_navigation(self):
        """Test that detail view provides prev/next entry IDs for navigation."""
        self.client.login(username='testuser', password='testpass123')
        # Entry2 is in the middle (ordered by date desc: entry3, entry2, entry1)
        url = reverse('health:timeline_detail', args=[self.entry2.id])
        response = self.client.get(url)

        # prev = older entry (entry1), next = newer entry (entry3)
        self.assertEqual(response.context['prev_entry_id'], self.entry1.id)
        self.assertEqual(response.context['next_entry_id'], self.entry3.id)

    def test_detail_first_entry_has_no_next(self):
        """Test that the newest entry has no 'next' entry."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('health:timeline_detail', args=[self.entry3.id])
        response = self.client.get(url)

        # entry3 is newest, so no next but has prev
        self.assertIsNone(response.context['next_entry_id'])
        self.assertEqual(response.context['prev_entry_id'], self.entry2.id)

    def test_detail_last_entry_has_no_prev(self):
        """Test that the oldest entry has no 'prev' entry."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('health:timeline_detail', args=[self.entry1.id])
        response = self.client.get(url)

        # entry1 is oldest, so no prev but has next
        self.assertIsNone(response.context['prev_entry_id'])
        self.assertEqual(response.context['next_entry_id'], self.entry2.id)

    def test_detail_shows_position_and_total(self):
        """Test that detail view shows position (e.g., '2 of 3')."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('health:timeline_detail', args=[self.entry2.id])
        response = self.client.get(url)

        self.assertEqual(response.context['entry_position'], 2)
        self.assertEqual(response.context['total_entries'], 3)

    def test_detail_404_for_other_user(self):
        """Test that users cannot view other users' entries."""
        other_user = User.objects.create_user(
            username='otheruser', password='testpass456'
        )
        self.client.login(username='otheruser', password='testpass456')
        url = reverse('health:timeline_detail', args=[self.entry1.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 404)


class TimelineCreateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.create_url = reverse('health:timeline_create')

    def test_create_requires_login(self):
        response = self.client.get(self.create_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.create_url}")

    def test_create_form_get(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/timeline_form.html')

    def test_create_entry_post(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'date': date.today().isoformat(),
            'time': '10:30',
            'entry_type': 'vet_visit',
            'title': 'New Test Entry',
            'content': 'Test content here',
            'bruno_mood': 'good',
            'tags': 'test, entry'
        }
        response = self.client.post(self.create_url, data)

        # Should redirect to detail view
        self.assertEqual(response.status_code, 302)

        # Entry should exist
        entry = TimelineEntry.objects.get(title='New Test Entry')
        self.assertEqual(entry.entry_type, 'vet_visit')
        self.assertEqual(entry.bruno_mood, 'good')


class TimelineEditViewTests(TestCase):
    """Tests for timeline entry edit functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='otherpass123'
        )
        self.entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            time=time(10, 30),
            entry_type='vet_visit',
            title='Original Title',
            content='Original content',
            bruno_mood='good'
        )
        self.edit_url = reverse('health:timeline_edit', args=[self.entry.id])

    def test_edit_requires_login(self):
        """Test that edit view requires authentication."""
        response = self.client.get(self.edit_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.edit_url}")

    def test_edit_form_get(self):
        """Test that edit form loads successfully."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/timeline_form.html')
        self.assertContains(response, 'Original Title')

    def test_edit_form_context(self):
        """Test that edit form has correct context data."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.context['entry'], self.entry)
        self.assertIn('providers', response.context)
        self.assertIn('entry_types', response.context)
        self.assertIn('mood_choices', response.context)

    def test_edit_entry_post(self):
        """Test that editing an entry works correctly."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'date': date.today().isoformat(),
            'time': '14:00',
            'entry_type': 'treatment',
            'title': 'Updated Title',
            'content': 'Updated content',
            'bruno_mood': 'great',
            'tags': 'updated, test'
        }
        response = self.client.post(self.edit_url, data)

        # Should redirect to detail view
        self.assertEqual(response.status_code, 302)

        # Entry should be updated
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.title, 'Updated Title')
        self.assertEqual(self.entry.content, 'Updated content')
        self.assertEqual(self.entry.entry_type, 'treatment')
        self.assertEqual(self.entry.bruno_mood, 'great')

    def test_edit_404_for_other_user(self):
        """Test that users cannot edit other users' entries."""
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 404)

    def test_edit_nonexistent_entry(self):
        """Test that editing nonexistent entry returns 404."""
        self.client.login(username='testuser', password='testpass123')
        bad_url = reverse('health:timeline_edit', args=[99999])
        response = self.client.get(bad_url)
        self.assertEqual(response.status_code, 404)


class ProviderViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.provider_list_url = reverse('health:provider_list')

    def test_provider_list_requires_login(self):
        response = self.client.get(self.provider_list_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.provider_list_url}")

    def test_provider_list_authenticated(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.provider_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/providers.html')

    def test_create_provider(self):
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'Dr. New Provider',
            'clinic_name': 'New Clinic',
            'location': 'Test City',
            'trust_rating': 4
        }
        response = self.client.post(reverse('health:provider_create'), data)

        # Should redirect to provider list
        self.assertEqual(response.status_code, 302)

        # Provider should exist
        provider = Provider.objects.get(name='Dr. New Provider')
        self.assertEqual(provider.trust_rating, 4)


class LoginViewTests(TestCase):
    """Tests for login/logout functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.login_url = reverse('health:login')
        self.logout_url = reverse('health:logout')

    def test_login_page_renders(self):
        """Test that login page renders correctly."""
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/login.html')

    def test_login_success(self):
        """Test successful login redirects to tracker."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('health:tracker'))

    def test_login_failure(self):
        """Test failed login shows error."""
        response = self.client.post(self.login_url, {
            'username': 'testuser',
            'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Invalid credentials')

    def test_login_redirect_if_authenticated(self):
        """Test that authenticated users are redirected from login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.login_url)
        self.assertRedirects(response, reverse('health:tracker'))

    def test_logout(self):
        """Test logout redirects to login page."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.logout_url)
        self.assertRedirects(response, self.login_url)


class DashboardViewTests(TestCase):
    """Tests for dashboard view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.dashboard_url = reverse('health:dashboard')

    def test_dashboard_requires_login(self):
        """Test that dashboard requires authentication."""
        response = self.client.get(self.dashboard_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.dashboard_url}")


class HistoryViewTests(TestCase):
    """Tests for history view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.history_url = reverse('health:history')

    def test_history_requires_login(self):
        """Test that history view requires authentication."""
        response = self.client.get(self.history_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.history_url}")

    def test_history_renders(self):
        """Test that history view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/history.html')

    def test_history_shows_entries(self):
        """Test that history view shows daily entries."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(user=self.user, date=date.today(), good_day='yes')
        response = self.client.get(self.history_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('entries', response.context)


class MedicationsViewTests(TestCase):
    """Tests for medications view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.medications_url = reverse('health:medications')

    def test_medications_requires_login(self):
        """Test that medications view requires authentication."""
        response = self.client.get(self.medications_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.medications_url}")

    def test_medications_renders(self):
        """Test that medications view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.medications_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/medications.html')

    def test_medications_context(self):
        """Test that medications view has correct context."""
        self.client.login(username='testuser', password='testpass123')
        Medication.objects.create(name='Test Med', dosage='10mg', frequency='daily', active=True)
        response = self.client.get(self.medications_url)
        self.assertIn('medications', response.context)


class AddMedicationViewTests(TestCase):
    """Tests for add medication functionality."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.add_med_url = reverse('health:add_medication')

    def test_add_medication_requires_login(self):
        """Test that add medication requires authentication."""
        response = self.client.post(self.add_med_url, {})
        self.assertEqual(response.status_code, 302)

    def test_add_medication_post(self):
        """Test adding a new medication via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'name': 'New Med',
            'dosage': '20mg',
            'frequency': 'twice daily',
            'notes': 'Test notes'
        }
        response = self.client.post(
            self.add_med_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(Medication.objects.filter(name='New Med').exists())


class RecordDoseViewTests(TestCase):
    """Tests for recording medication doses."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.medication = Medication.objects.create(
            name='Test Med', dosage='10mg', frequency='daily', active=True
        )

    def test_record_dose_requires_login(self):
        """Test that recording dose requires authentication."""
        url = reverse('health:record_dose', args=[self.medication.id])
        response = self.client.post(url, {})
        self.assertEqual(response.status_code, 302)

    def test_record_dose_post(self):
        """Test recording a medication dose returns JSON."""
        self.client.login(username='testuser', password='testpass123')
        url = reverse('health:record_dose', args=[self.medication.id])
        response = self.client.post(url, {}, content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(MedicationDose.objects.filter(medication=self.medication).exists())


class NodesViewTests(TestCase):
    """Tests for lymph node tracking view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.nodes_url = reverse('health:nodes')

    def test_nodes_requires_login(self):
        """Test that nodes view requires authentication."""
        response = self.client.get(self.nodes_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.nodes_url}")

    def test_nodes_renders(self):
        """Test that nodes view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.nodes_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/nodes.html')


class CBPIViewTests(TestCase):
    """Tests for CBPI assessment view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.cbpi_url = reverse('health:cbpi')
        self.save_cbpi_url = reverse('health:save_cbpi')

    def test_cbpi_requires_login(self):
        """Test that CBPI view requires authentication."""
        response = self.client.get(self.cbpi_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.cbpi_url}")

    def test_cbpi_renders(self):
        """Test that CBPI view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.cbpi_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/cbpi.html')

    def test_save_cbpi_requires_login(self):
        """Test that save CBPI requires authentication."""
        response = self.client.post(self.save_cbpi_url, {})
        self.assertEqual(response.status_code, 302)

    def test_save_cbpi_post(self):
        """Test saving CBPI assessment via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'worst_pain': 5,
            'least_pain': 2,
            'average_pain': 3,
            'current_pain': 4,
            'general_activity': 4,
            'enjoyment_of_life': 3,
            'ability_to_rise': 4,
            'ability_to_walk': 3,
            'ability_to_run': 5,
            'ability_to_climb': 4,
            'overall_quality_of_life': 6,
            'notes': 'Test CBPI'
        }
        response = self.client.post(
            self.save_cbpi_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(CBPIAssessment.objects.filter(user=self.user).exists())


class CORQViewTests(TestCase):
    """Tests for CORQ assessment view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.corq_url = reverse('health:corq')
        self.save_corq_url = reverse('health:save_corq')

    def test_corq_requires_login(self):
        """Test that CORQ view requires authentication."""
        response = self.client.get(self.corq_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.corq_url}")

    def test_corq_renders(self):
        """Test that CORQ view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.corq_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/corq.html')

    def test_save_corq_requires_login(self):
        """Test that save CORQ requires authentication."""
        response = self.client.post(self.save_corq_url, {})
        self.assertEqual(response.status_code, 302)

    def test_save_corq_post(self):
        """Test saving CORQ assessment via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'energy_level': 3,
            'playfulness': 4,
            'interest_in_surroundings': 3,
            'appetite': 4,
            'seeks_attention': 4,
            'enjoys_interaction': 3,
            'greets_family': 4,
            'tail_wagging': 3,
            'shows_pain': 2,
            'vocalizes_pain': 1,
            'avoids_touch': 2,
            'pants_restless': 1,
            'walks_normally': 3,
            'rises_easily': 4,
            'climbs_stairs': 3,
            'jumps': 4,
            'global_qol': 7,
            'notes': 'Test CORQ'
        }
        response = self.client.post(
            self.save_corq_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(CORQAssessment.objects.filter(user=self.user).exists())


class TreatmentsViewTests(TestCase):
    """Tests for treatments view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.treatments_url = reverse('health:treatments')
        self.save_treatment_url = reverse('health:save_treatment')

    def test_treatments_requires_login(self):
        """Test that treatments view requires authentication."""
        response = self.client.get(self.treatments_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.treatments_url}")

    def test_treatments_renders(self):
        """Test that treatments view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.treatments_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/treatments.html')

    def test_save_treatment_requires_login(self):
        """Test that save treatment requires authentication."""
        response = self.client.post(self.save_treatment_url, {})
        self.assertEqual(response.status_code, 302)

    def test_save_treatment_post(self):
        """Test saving treatment session via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'date': date.today().isoformat(),
            'treatment_type': 'chemotherapy',
            'protocol': 'CHOP',
            'cycle_number': 1,
            'agent': 'Vincristine',
            'dose': '0.5 mg/kg',
            'notes': 'Test treatment'
        }
        response = self.client.post(
            self.save_treatment_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(TreatmentSession.objects.filter(user=self.user).exists())


class EventsViewTests(TestCase):
    """Tests for adverse events view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.events_url = reverse('health:events')
        self.save_event_url = reverse('health:save_event')

    def test_events_requires_login(self):
        """Test that events view requires authentication."""
        response = self.client.get(self.events_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.events_url}")

    def test_events_renders(self):
        """Test that events view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.events_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/events.html')

    def test_save_event_requires_login(self):
        """Test that save event requires authentication."""
        response = self.client.post(self.save_event_url, {})
        self.assertEqual(response.status_code, 302)

    def test_save_event_post(self):
        """Test saving adverse event via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'date': date.today().isoformat(),
            'category': 'GI',
            'event': 'Vomiting',
            'grade': 2,
            'treatment': 'Ondansetron',
            'intervention': 'Medication given',
            'notes': 'Test event'
        }
        response = self.client.post(
            self.save_event_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(VCOGCTCAEEvent.objects.filter(user=self.user).exists())


class NutritionViewTests(TestCase):
    """Tests for nutrition tracking view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.nutrition_url = reverse('health:nutrition')

    def test_nutrition_requires_login(self):
        """Test that nutrition view requires authentication."""
        response = self.client.get(self.nutrition_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.nutrition_url}")

    def test_nutrition_renders(self):
        """Test that nutrition view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.nutrition_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/nutrition.html')


class FoodDatabaseViewTests(TestCase):
    """Tests for food database view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.food_db_url = reverse('health:food_database')

    def test_food_database_requires_login(self):
        """Test that food database view requires authentication."""
        response = self.client.get(self.food_db_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.food_db_url}")

    def test_food_database_renders(self):
        """Test that food database view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.food_db_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/food_database.html')


class MealPlanningViewTests(TestCase):
    """Tests for meal planning view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.meal_planning_url = reverse('health:meal_planning')

    def test_meal_planning_requires_login(self):
        """Test that meal planning view requires authentication."""
        response = self.client.get(self.meal_planning_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.meal_planning_url}")

    def test_meal_planning_renders(self):
        """Test that meal planning view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.meal_planning_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/meal_planning.html')


class RecordsViewTests(TestCase):
    """Tests for medical records view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.records_url = reverse('health:records')

    def test_records_requires_login(self):
        """Test that records view requires authentication."""
        response = self.client.get(self.records_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.records_url}")

    def test_records_renders(self):
        """Test that records view renders."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.records_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/records.html')


class APIChartDataTests(TestCase):
    """Tests for chart data API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.chart_url = reverse('health:api_chart_data')

    def test_chart_data_requires_login(self):
        """Test that chart data API requires authentication."""
        response = self.client.get(self.chart_url)
        self.assertEqual(response.status_code, 302)

    def test_chart_data_returns_json(self):
        """Test that chart data API returns JSON."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.chart_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class APIFoodsTests(TestCase):
    """Tests for foods API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.foods_url = reverse('health:api_foods')

    def test_api_foods_requires_login(self):
        """Test that foods API requires authentication."""
        response = self.client.get(self.foods_url)
        self.assertEqual(response.status_code, 302)

    def test_api_foods_returns_json(self):
        """Test that foods API returns JSON."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.foods_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class APINutritionSummaryTests(TestCase):
    """Tests for nutrition summary API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.summary_url = reverse('health:api_nutrition_summary')

    def test_api_nutrition_summary_requires_login(self):
        """Test that nutrition summary API requires authentication."""
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, 302)

    def test_api_nutrition_summary_returns_json(self):
        """Test that nutrition summary API returns JSON."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.summary_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class SetLanguageViewTests(TestCase):
    """Tests for language switching."""

    def setUp(self):
        self.client = Client()
        self.set_language_url = reverse('health:set_language')

    def test_set_language_post(self):
        """Test setting language preference."""
        response = self.client.post(self.set_language_url, {
            'language': 'es',
            'next': '/'
        })
        self.assertEqual(response.status_code, 302)


class TimelineDeleteViewTests(TestCase):
    """Tests for timeline entry deletion."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='otherpass123'
        )
        self.entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Test Entry',
            content='Test content'
        )
        self.delete_url = reverse('health:timeline_delete', args=[self.entry.id])

    def test_delete_requires_login(self):
        """Test that delete requires authentication."""
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)

    def test_delete_requires_post(self):
        """Test that delete only works with POST."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.delete_url)
        self.assertEqual(response.status_code, 405)

    def test_delete_entry(self):
        """Test deleting a timeline entry."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TimelineEntry.objects.filter(id=self.entry.id).exists())

    def test_delete_404_for_other_user(self):
        """Test that users cannot delete other users' entries."""
        self.client.login(username='otheruser', password='otherpass123')
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 404)


class SaveDailyEntryViewTests(TestCase):
    """Tests for saving daily entry."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_entry')

    def test_save_requires_login(self):
        """Test that saving requires authentication."""
        response = self.client.post(self.save_url, {})
        self.assertEqual(response.status_code, 302)

    def test_save_daily_entry_post(self):
        """Test saving daily entry via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'good_day': 'yes',
            'tail_body_language': 4,
            'interest_people': 4,
            'appetite': 5,
            'energy_level': 3,
            'notes': 'Test notes'
        }
        response = self.client.post(
            self.save_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class SaveNodeMeasurementViewTests(TestCase):
    """Tests for saving node measurements."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_nodes')

    def test_save_requires_login(self):
        """Test that saving requires authentication."""
        response = self.client.post(self.save_url, {})
        self.assertEqual(response.status_code, 302)

    def test_save_node_measurement_post(self):
        """Test saving node measurement via JSON API."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'mandibular_left': 2.5,
            'mandibular_right': 2.3,
            'popliteal_left': 1.8,
            'popliteal_right': 1.9
        }
        response = self.client.post(
            self.save_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        self.assertTrue(LymphNodeMeasurement.objects.filter(user=self.user).exists())


class SaveMealViewTests(TestCase):
    """Tests for saving meals."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_meal')

    def test_save_requires_login(self):
        """Test that saving requires authentication."""
        response = self.client.post(self.save_url, {})
        self.assertEqual(response.status_code, 302)


class SaveSupplementViewTests(TestCase):
    """Tests for saving supplements."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_supplement')

    def test_save_requires_login(self):
        """Test that saving requires authentication."""
        response = self.client.post(self.save_url, {})
        self.assertEqual(response.status_code, 302)


class UpdateWeightViewTests(TestCase):
    """Tests for updating weight."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.update_url = reverse('health:update_weight')

    def test_update_requires_login(self):
        """Test that update requires authentication."""
        response = self.client.post(self.update_url, {})
        self.assertEqual(response.status_code, 302)


class APILabValuesTests(TestCase):
    """Tests for lab values API endpoint."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.lab_values_url = reverse('health:api_lab_values')

    def test_api_lab_values_requires_login(self):
        """Test that lab values API requires authentication."""
        response = self.client.get(self.lab_values_url)
        self.assertEqual(response.status_code, 302)

    def test_api_lab_values_returns_json(self):
        """Test that lab values API returns JSON."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.lab_values_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')


class DashboardViewWithDataTests(TestCase):
    """Tests for dashboard view with actual data."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.dashboard_url = reverse('health:dashboard')

    def test_dashboard_with_daily_entry(self):
        """Test dashboard shows today's entry data."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes',
            appetite=4,
            energy_level=4,
            tail_body_language=4,
            interest_people=4
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('today_entry', response.context)

    def test_dashboard_with_cbpi_assessment(self):
        """Test dashboard shows CBPI data."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes'
        )
        CBPIAssessment.objects.create(
            user=self.user,
            date=date.today(),
            worst_pain=3,
            least_pain=1,
            average_pain=2,
            current_pain=2,
            general_activity=3,
            enjoyment_of_life=2,
            ability_to_rise=2,
            ability_to_walk=2,
            ability_to_run=3,
            ability_to_climb=3,
            overall_quality_of_life=3
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_with_corq_assessment(self):
        """Test dashboard shows CORQ data."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes'
        )
        CORQAssessment.objects.create(
            user=self.user,
            date=date.today(),
            energy_level=3,
            playfulness=3,
            appetite=4,
            interest_in_surroundings=3,
            seeks_attention=3,
            enjoys_interaction=4,
            greets_family=4,
            tail_wagging=4,
            shows_pain=2,
            vocalizes_pain=1,
            avoids_touch=1,
            pants_restless=2,
            walks_normally=4,
            rises_easily=3,
            climbs_stairs=3,
            jumps=3,
            global_qol=70
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_with_lymph_nodes(self):
        """Test dashboard shows lymph node data."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes'
        )
        LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date.today(),
            mandibular_left=Decimal('2.5'),
            mandibular_right=Decimal('2.3')
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)


class APIChartDataExtendedTests(TestCase):
    """Extended tests for chart data API with different chart types."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.chart_url = reverse('health:api_chart_data')

    def test_cbpi_chart_data(self):
        """Test CBPI chart data retrieval."""
        self.client.login(username='testuser', password='testpass123')
        CBPIAssessment.objects.create(
            user=self.user,
            date=date.today(),
            worst_pain=5,
            least_pain=2,
            average_pain=3,
            current_pain=3,
            general_activity=4,
            enjoyment_of_life=3,
            ability_to_rise=2,
            ability_to_walk=2,
            ability_to_run=4,
            ability_to_climb=4,
            overall_quality_of_life=3
        )
        response = self.client.get(self.chart_url, {'type': 'cbpi', 'days': '30'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('severity', data)
        self.assertIn('interference', data)

    def test_corq_chart_data(self):
        """Test CORQ chart data retrieval."""
        self.client.login(username='testuser', password='testpass123')
        CORQAssessment.objects.create(
            user=self.user,
            date=date.today(),
            energy_level=3,
            playfulness=3,
            appetite=4,
            interest_in_surroundings=3,
            seeks_attention=3,
            enjoys_interaction=4,
            greets_family=4,
            tail_wagging=4,
            shows_pain=2,
            vocalizes_pain=1,
            avoids_touch=1,
            pants_restless=2,
            walks_normally=4,
            rises_easily=3,
            climbs_stairs=3,
            jumps=3,
            global_qol=70
        )
        response = self.client.get(self.chart_url, {'type': 'corq', 'days': '30'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('vitality', data)

    def test_nodes_chart_data(self):
        """Test lymph node chart data retrieval."""
        self.client.login(username='testuser', password='testpass123')
        LymphNodeMeasurement.objects.create(
            user=self.user,
            date=date.today(),
            mandibular_left=Decimal('2.5'),
            mandibular_right=Decimal('2.3'),
            popliteal_left=Decimal('1.8'),
            popliteal_right=Decimal('1.9')
        )
        response = self.client.get(self.chart_url, {'type': 'nodes', 'days': '30'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('mandibular_left', data)

    def test_events_chart_data(self):
        """Test adverse events chart data retrieval."""
        self.client.login(username='testuser', password='testpass123')
        VCOGCTCAEEvent.objects.create(
            user=self.user,
            date=date.today(),
            category='gastrointestinal',
            event='vomiting',
            grade=2
        )
        response = self.client.get(self.chart_url, {'type': 'events', 'days': '30'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('grades', data)
        self.assertIn('categories', data)

    def test_unknown_chart_type(self):
        """Test unknown chart type returns error."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.chart_url, {'type': 'unknown', 'days': '30'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('error', data)


class SaveMealWithItemsTests(TestCase):
    """Tests for saving meals with items."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_meal')
        self.food = Food.objects.create(
            name='Chicken Breast',
            category='protein',
            protein_g_per_100g=Decimal('31.0'),
            fat_g_per_100g=Decimal('3.6'),
            carbs_g_per_100g=Decimal('0.0'),
            status='approved'
        )

    def test_save_meal_with_items(self):
        """Test saving a meal with food items."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'meal_type': 'breakfast',
            'date': str(date.today()),
            'appetite': 'good',
            'items': [
                {'food_id': self.food.id, 'amount_g': 100}
            ]
        }
        response = self.client.post(
            self.save_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertTrue(Meal.objects.filter(user=self.user).exists())

    def test_save_meal_blocked_food_warning(self):
        """Test saving meal with blocked food returns warning."""
        self.client.login(username='testuser', password='testpass123')
        blocked_food = Food.objects.create(
            name='Grapes',
            category='other',
            protein_g_per_100g=Decimal('0.7'),
            fat_g_per_100g=Decimal('0.2'),
            carbs_g_per_100g=Decimal('18.0'),
            status='blocked',
            warning='Toxic to dogs'
        )
        data = {
            'meal_type': 'breakfast',
            'date': str(date.today()),
            'items': [
                {'food_id': blocked_food.id, 'amount_g': 50}
            ]
        }
        response = self.client.post(
            self.save_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'warning')


class SaveSupplementWithDataTests(TestCase):
    """Tests for saving supplements with complete data."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.save_url = reverse('health:save_supplement')

    def test_save_supplement_calcium(self):
        """Test saving a calcium supplement."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'supplement_type': 'calcium',
            'date': str(date.today()),
            'product_name': 'NOW Calcium Carbonate',
            'dose_amount': '1 tablet',
            'calcium_mg': 600
        }
        response = self.client.post(
            self.save_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertTrue(SupplementDose.objects.filter(user=self.user).exists())

    def test_save_supplement_fish_oil(self):
        """Test saving a fish oil supplement."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'supplement_type': 'fish_oil',
            'date': str(date.today()),
            'product_name': 'Nordic Naturals',
            'dose_amount': '2 softgels',
            'epa_mg': 650,
            'dha_mg': 450
        }
        response = self.client.post(
            self.save_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertIn('omega3_total', response_data)


class UpdateWeightWithDataTests(TestCase):
    """Tests for updating weight with complete data."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.update_url = reverse('health:update_weight')

    def test_update_weight_creates_profile(self):
        """Test updating weight creates profile if not exists."""
        self.client.login(username='testuser', password='testpass123')
        data = {
            'weight_kg': 31.5
        }
        response = self.client.post(
            self.update_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        response_data = json.loads(response.content)
        self.assertEqual(response_data['status'], 'success')
        self.assertTrue(DogProfile.objects.filter(user=self.user).exists())

    def test_update_weight_updates_existing(self):
        """Test updating weight updates existing profile."""
        self.client.login(username='testuser', password='testpass123')
        DogProfile.objects.create(
            user=self.user,
            name='Bruno',
            weight_kg=Decimal('30.0')
        )
        data = {
            'weight_kg': 31.5,
            'target_weight_kg': 32.0
        }
        response = self.client.post(
            self.update_url,
            json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        profile = DogProfile.objects.get(user=self.user)
        self.assertEqual(float(profile.weight_kg), 31.5)


class APINutritionSummaryWithDataTests(TestCase):
    """Tests for nutrition summary API with actual data."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.nutrition_url = reverse('health:api_nutrition_summary')

    def test_nutrition_summary_with_meals(self):
        """Test nutrition summary returns meal data."""
        self.client.login(username='testuser', password='testpass123')
        meal = Meal.objects.create(
            user=self.user,
            date=date.today(),
            meal_type='breakfast',
            appetite='good'
        )
        food = Food.objects.create(
            name='Test Food',
            category='protein',
            protein_g_per_100g=Decimal('20.0'),
            fat_g_per_100g=Decimal('10.0'),
            carbs_g_per_100g=Decimal('5.0'),
            status='approved'
        )
        MealItem.objects.create(
            meal=meal,
            food=food,
            amount_g=Decimal('100.0')
        )
        response = self.client.get(self.nutrition_url, {'days': '7'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('labels', data)
        self.assertIn('food_g', data)


class RecordViewsTests(TestCase):
    """Tests for medical record views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )
        self.records_url = reverse('health:records')

    def test_records_view_with_lab_values(self):
        """Test records view shows lab values."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        LabValue.objects.create(
            medical_record=record,
            user=self.user,
            date=date.today(),
            test_name='wbc',
            value=Decimal('8.5'),
            unit='K/uL'
        )
        response = self.client.get(self.records_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('lab_trends', response.context)

    def test_record_detail_view(self):
        """Test record detail view."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        detail_url = reverse('health:record_detail', args=[record.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('record', response.context)

    def test_record_detail_other_user_404(self):
        """Test record detail returns 404 for other user's record."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.other_user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        detail_url = reverse('health:record_detail', args=[record.id])
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, 404)

    def test_edit_record_get(self):
        """Test edit record form loads."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        edit_url = reverse('health:edit_record', args=[record.id])
        response = self.client.get(edit_url)
        self.assertEqual(response.status_code, 200)

    def test_edit_record_post(self):
        """Test editing a record."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        edit_url = reverse('health:edit_record', args=[record.id])
        response = self.client.post(edit_url, {
            'record_type': 'imaging',
            'title': 'X-Ray',
            'date': str(date.today()),
            'source': 'clinic'
        })
        self.assertEqual(response.status_code, 302)
        record.refresh_from_db()
        self.assertEqual(record.record_type, 'imaging')
        self.assertEqual(record.title, 'X-Ray')

    def test_delete_record(self):
        """Test deleting a record."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        delete_url = reverse('health:delete_record', args=[record.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(MedicalRecord.objects.filter(id=record.id).exists())

    def test_delete_record_ajax(self):
        """Test deleting a record via AJAX."""
        self.client.login(username='testuser', password='testpass123')
        record = MedicalRecord.objects.create(
            user=self.user,
            date=date.today(),
            record_type='lab_work',
            title='Blood Panel'
        )
        delete_url = reverse('health:delete_record', args=[record.id])
        response = self.client.post(
            delete_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')


class TimelineDeleteAttachmentTests(TestCase):
    """Tests for deleting timeline attachments."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.other_user = User.objects.create_user(
            username='otheruser', password='testpass123'
        )
        self.entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Test Entry',
            content='Test content'
        )
        self.attachment = TimelineAttachment.objects.create(
            timeline_entry=self.entry,
            title='test.pdf',
            file_type='document'
        )

    def test_delete_attachment_requires_login(self):
        """Test delete attachment requires authentication."""
        delete_url = reverse('health:timeline_delete_attachment', args=[self.attachment.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)

    def test_delete_attachment_not_owner(self):
        """Test delete attachment fails for non-owner."""
        self.client.login(username='otheruser', password='testpass123')
        delete_url = reverse('health:timeline_delete_attachment', args=[self.attachment.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 403)

    def test_delete_attachment_success(self):
        """Test delete attachment succeeds for owner."""
        self.client.login(username='testuser', password='testpass123')
        delete_url = reverse('health:timeline_delete_attachment', args=[self.attachment.id])
        response = self.client.post(delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(TimelineAttachment.objects.filter(id=self.attachment.id).exists())

    def test_delete_attachment_ajax(self):
        """Test delete attachment via AJAX."""
        self.client.login(username='testuser', password='testpass123')
        attachment = TimelineAttachment.objects.create(
            timeline_entry=self.entry,
            title='test2.pdf',
            file_type='document'
        )
        delete_url = reverse('health:timeline_delete_attachment', args=[attachment.id])
        response = self.client.post(
            delete_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')


class ProviderViewsTests(TestCase):
    """Tests for provider views."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.provider_list_url = reverse('health:provider_list')
        self.provider_create_url = reverse('health:provider_create')

    def test_provider_list_view(self):
        """Test provider list view."""
        self.client.login(username='testuser', password='testpass123')
        Provider.objects.create(name='Dr. Smith', trust_rating=5)
        response = self.client.get(self.provider_list_url)
        self.assertEqual(response.status_code, 200)
        self.assertIn('providers', response.context)

    def test_provider_create_get(self):
        """Test provider create form loads."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.provider_create_url)
        self.assertEqual(response.status_code, 200)

    def test_provider_create_post(self):
        """Test creating a new provider."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.provider_create_url, {
            'name': 'Dr. Johnson',
            'clinic_name': 'Pet Clinic',
            'trust_rating': '4',
            'specialty': 'Oncology'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Provider.objects.filter(name='Dr. Johnson').exists())

    def test_provider_edit_get(self):
        """Test provider edit form loads with existing provider."""
        self.client.login(username='testuser', password='testpass123')
        provider = Provider.objects.create(name='Dr. Smith', trust_rating=5)
        response = self.client.get(f'{self.provider_create_url}?id={provider.id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['provider'], provider)

    def test_provider_edit_post(self):
        """Test editing an existing provider."""
        self.client.login(username='testuser', password='testpass123')
        provider = Provider.objects.create(name='Dr. Smith', trust_rating=5)
        response = self.client.post(f'{self.provider_create_url}?id={provider.id}', {
            'name': 'Dr. Smith Jr.',
            'clinic_name': 'New Clinic',
            'trust_rating': '4'
        })
        self.assertEqual(response.status_code, 302)
        provider.refresh_from_db()
        self.assertEqual(provider.name, 'Dr. Smith Jr.')
        self.assertEqual(provider.clinic_name, 'New Clinic')


class UploadRecordTests(TestCase):
    """Tests for uploading medical records."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.upload_url = reverse('health:upload_record')

    def test_upload_requires_login(self):
        """Test that upload requires authentication."""
        response = self.client.post(self.upload_url, {})
        self.assertEqual(response.status_code, 302)

    def test_upload_without_file(self):
        """Test upload without file returns error."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.upload_url, {
            'record_type': 'lab_work',
            'date': str(date.today()),
            'title': 'Test Record'
        })
        self.assertEqual(response.status_code, 400)


class APILabValuesExtendedTests(TestCase):
    """Extended tests for lab values API."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.lab_values_url = reverse('health:api_lab_values')

    def test_api_lab_values_with_test_name(self):
        """Test lab values API with specific test name."""
        self.client.login(username='testuser', password='testpass123')
        LabValue.objects.create(
            user=self.user,
            date=date.today(),
            test_name='wbc',
            value=Decimal('8.5'),
            unit='K/uL'
        )
        response = self.client.get(self.lab_values_url, {'test': 'wbc'})
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('wbc', data)
        self.assertIn('values', data['wbc'])


class TimelineCreatePostTests(TestCase):
    """Tests for timeline entry creation with POST."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.create_url = reverse('health:timeline_create')

    def test_create_entry_post(self):
        """Test creating timeline entry via POST."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.create_url, {
            'date': str(date.today()),
            'entry_type': 'vet_visit',
            'title': 'Annual Checkup',
            'content': 'Bruno had his annual checkup today.',
            'bruno_mood': 'good'
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(TimelineEntry.objects.filter(title='Annual Checkup').exists())


class TimelineEditPostTests(TestCase):
    """Tests for timeline entry editing with POST."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Original Title',
            content='Original content'
        )
        self.edit_url = reverse('health:timeline_edit', args=[self.entry.id])

    def test_edit_entry_post(self):
        """Test editing timeline entry via POST."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.post(self.edit_url, {
            'date': str(date.today()),
            'entry_type': 'lab_result',
            'title': 'Updated Title',
            'content': 'Updated content',
            'bruno_mood': 'great'
        })
        self.assertEqual(response.status_code, 302)
        self.entry.refresh_from_db()
        self.assertEqual(self.entry.title, 'Updated Title')
        self.assertEqual(self.entry.entry_type, 'lab_result')


class TimelineDeleteWithAjaxTests(TestCase):
    """Tests for timeline deletion with AJAX."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.entry = TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Test Entry',
            content='Test content'
        )

    def test_delete_entry_ajax(self):
        """Test deleting timeline entry via AJAX."""
        self.client.login(username='testuser', password='testpass123')
        delete_url = reverse('health:timeline_delete', args=[self.entry.id])
        response = self.client.post(
            delete_url,
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['status'], 'success')
        self.assertFalse(TimelineEntry.objects.filter(id=self.entry.id).exists())


class DashboardQolStatusTests(TestCase):
    """Tests for dashboard QoL status colors."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.dashboard_url = reverse('health:dashboard')

    def test_dashboard_green_status(self):
        """Test dashboard shows green status for high score."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes',
            tail_body_language=5,
            interest_people=5,
            interest_environment=5,
            enjoyment_favorites=5,
            overall_spark=5,
            appetite=5,
            food_enjoyment=5,
            energy_level=5,
            willingness_move=5
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['qol_status'], 'green')

    def test_dashboard_red_status(self):
        """Test dashboard shows red status for low score."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='no',
            tail_body_language=1,
            interest_people=1,
            interest_environment=1,
            enjoyment_favorites=1,
            overall_spark=1,
            appetite=1,
            food_enjoyment=1,
            energy_level=1,
            willingness_move=1
        )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['qol_status'], 'red')

    def test_dashboard_trend_calculation(self):
        """Test dashboard trend calculation."""
        self.client.login(username='testuser', password='testpass123')
        DailyEntry.objects.create(
            user=self.user,
            date=date.today(),
            good_day='yes'
        )
        for i in range(1, 8):
            DailyEntry.objects.create(
                user=self.user,
                date=date.today() - timedelta(days=i),
                good_day='yes',
                tail_body_language=4,
                interest_people=4
            )
        response = self.client.get(self.dashboard_url)
        self.assertEqual(response.status_code, 200)


# ============================================================================
# Calendar View Tests
# ============================================================================

class CalendarMonthViewTests(TestCase):
    """Tests for calendar month view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.calendar_url = reverse('health:calendar')

    def test_calendar_requires_login(self):
        """Calendar view requires authentication."""
        response = self.client.get(self.calendar_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.calendar_url}")

    def test_calendar_authenticated(self):
        """Authenticated users can access calendar."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.calendar_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'health/calendar.html')

    def test_calendar_context_has_weeks(self):
        """Calendar context includes weeks array."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.calendar_url)
        self.assertIn('weeks', response.context)
        self.assertIn('year', response.context)
        self.assertIn('month', response.context)
        self.assertIn('month_name', response.context)
        self.assertEqual(response.context['view_mode'], 'month')

    def test_calendar_specific_month(self):
        """Can navigate to specific month."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('health:calendar_month', args=[2025, 6]))
        self.assertEqual(response.context['year'], 2025)
        self.assertEqual(response.context['month'], 6)
        self.assertEqual(response.context['month_name'], 'June')

    def test_calendar_shows_entries(self):
        """Calendar shows entries on correct days."""
        self.client.login(username='testuser', password='testpass123')
        TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Test Appointment'
        )
        response = self.client.get(self.calendar_url)
        # Find today in weeks
        found = False
        for week in response.context['weeks']:
            for day in week:
                if day['is_today'] and day['entries']:
                    found = True
                    self.assertEqual(len(day['entries']), 1)
                    self.assertEqual(day['entries'][0]['title'], 'Test Appointment')
        self.assertTrue(found)

    def test_calendar_navigation_links(self):
        """Calendar has prev/next month navigation."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('health:calendar_month', args=[2025, 6]))
        self.assertIn('prev_year', response.context)
        self.assertIn('prev_month', response.context)
        self.assertIn('next_year', response.context)
        self.assertIn('next_month', response.context)
        # June 2025 -> prev is May 2025, next is July 2025
        self.assertEqual(response.context['prev_month'], 5)
        self.assertEqual(response.context['next_month'], 7)

    def test_calendar_weeks_have_seven_days(self):
        """Each week in calendar has exactly 7 days."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.calendar_url)
        for week in response.context['weeks']:
            self.assertEqual(len(week), 7)

    def test_calendar_marks_today(self):
        """Calendar correctly marks today."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.calendar_url)
        today_found = False
        for week in response.context['weeks']:
            for day in week:
                if day['is_today']:
                    today_found = True
                    self.assertEqual(day['date'], date.today())
        self.assertTrue(today_found)


class CalendarWeekViewTests(TestCase):
    """Tests for calendar week view."""

    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser', password='testpass123'
        )
        self.week_url = reverse('health:calendar_week')

    def test_week_view_requires_login(self):
        """Week view requires authentication."""
        response = self.client.get(self.week_url)
        self.assertRedirects(response, f"{reverse('health:login')}?next={self.week_url}")

    def test_week_view_authenticated(self):
        """Authenticated users can access week view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.week_url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['view_mode'], 'week')

    def test_week_view_has_seven_days(self):
        """Week view shows exactly 7 days."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.week_url)
        self.assertIn('days', response.context)
        self.assertEqual(len(response.context['days']), 7)

    def test_week_view_shows_entries(self):
        """Week view shows entries on correct days."""
        self.client.login(username='testuser', password='testpass123')
        TimelineEntry.objects.create(
            user=self.user,
            date=date.today(),
            entry_type='vet_visit',
            title='Today Appointment'
        )
        response = self.client.get(self.week_url)
        today_found = False
        for day in response.context['days']:
            if day['is_today']:
                today_found = True
                self.assertEqual(len(day['entries']), 1)
        self.assertTrue(today_found)

    def test_week_view_navigation(self):
        """Week view has prev/next week navigation."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(self.week_url)
        self.assertIn('prev_year', response.context)
        self.assertIn('prev_week', response.context)
        self.assertIn('next_year', response.context)
        self.assertIn('next_week', response.context)
