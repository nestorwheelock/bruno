from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import json

from .models import DailyEntry, Medication, MedicationDose, LymphNodeMeasurement


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
