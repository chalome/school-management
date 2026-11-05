from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from core.models import SchoolYear

from .models import Child, ChildContact


class ChildModelTests(TestCase):
    def test_child_string_representation(self):
        child = Child.objects.create(
            first_name='Isabelle',
            last_name='Nkurunziza',
            birth_date=date(2022, 4, 12),
            emergency_contacts='Parent: +257 79 00 00 01',
            authorized_pickup_persons='Parent',
        )

        self.assertEqual(str(child), 'Isabelle Nkurunziza')
        self.assertTrue(child.student_number.startswith('PEG-'))

    def test_contacts_are_attached_to_the_child(self):
        child = Child.objects.create(
            first_name='Isabelle',
            last_name='Nkurunziza',
            birth_date=date(2022, 4, 12),
        )
        contact = ChildContact.objects.create(
            child=child,
            contact_type=ChildContact.ContactType.PICKUP,
            full_name='Aline Nkurunziza',
            relationship='Tante',
            phone='+257 79 00 00 01',
        )

        self.assertEqual(child.contacts.get(), contact)

    def test_child_screens_require_login_and_render(self):
        self.assertEqual(self.client.get(reverse('child_list')).status_code, 302)
        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )
        child = Child.objects.create(
            first_name='Isabelle',
            last_name='Nkurunziza',
            birth_date=date(2022, 4, 12),
        )

        self.assertEqual(self.client.get(reverse('child_list')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('child_detail', args=[child.pk])).status_code,
            200,
        )
        self.assertEqual(self.client.get(reverse('child_create')).status_code, 200)

    def test_registration_saves_a_child_and_authorized_pickup_contact(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )
        response = self.client.post(
            reverse('child_create'),
            {
                'first_name': 'Akimana',
                'last_name': 'Nkurunziza',
                'birth_date': '2022-07-14',
                'nationality': 'Burundaise',
                'preferred_hospital': 'Kira Hospital',
                'contacts-TOTAL_FORMS': '1',
                'contacts-INITIAL_FORMS': '0',
                'contacts-MIN_NUM_FORMS': '0',
                'contacts-MAX_NUM_FORMS': '1000',
                'contacts-0-contact_type': ChildContact.ContactType.PICKUP,
                'contacts-0-full_name': 'Aline Nkurunziza',
                'contacts-0-relationship': 'Tante',
                'contacts-0-phone': '+257 79 00 00 01',
            },
        )

        child = Child.objects.get(first_name='Akimana')
        self.assertRedirects(response, reverse('child_detail', args=[child.pk]))
        self.assertEqual(child.contacts.get().full_name, 'Aline Nkurunziza')
        self.assertEqual(
            child.enrollments.get().school_year,
            SchoolYear.objects.get(is_active=True),
        )
