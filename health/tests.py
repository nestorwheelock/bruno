from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import (
    DailyEntry, Medication, MedicationDose, LymphNodeMeasurement,
    Provider, TimelineEntry, TimelineAttachment
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
