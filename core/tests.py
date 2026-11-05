from datetime import date
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from children.models import Child
from payments.models import MonthlyFeePayment

from .models import (
    ChildEnrollment,
    ClassRoom,
    SchoolYear,
    next_school_year_dates,
    school_year_dates,
)


class ClassRoomModelTests(TestCase):
    def test_classroom_string_representation(self):
        classroom = ClassRoom.objects.create(
            name='Salle test',
            section_type=ClassRoom.SectionType.MATERNELLE,
        )

        self.assertEqual(str(classroom), 'Salle test (Maternelle)')

    def test_dashboard_requires_login_and_renders_classroom_data(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )
        classroom = ClassRoom.objects.create(
            name='Crèche test',
            section_type=ClassRoom.SectionType.CRECHE,
        )
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, classroom.name)

    def test_classroom_list_renders_and_create_page_is_available(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )

        self.assertEqual(self.client.get(reverse('classroom_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('classroom_create')).status_code, 200)


class SchoolYearTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='admin',
            password='SecureTestPass123!',
        )
        self.client.force_login(self.user)
        self.active_year = SchoolYear.objects.get(is_active=True)
        self.previous_year = SchoolYear.objects.create(
            start_date=date(2025, 9, 1),
            end_date=date(2026, 6, 30),
        )
        self.current_child = Child.objects.create(
            first_name='Amina',
            last_name='Active',
            birth_date=date(2022, 1, 1),
        )
        self.previous_child = Child.objects.create(
            first_name='Benoit',
            last_name='Previous',
            birth_date=date(2021, 1, 1),
        )
        self.classroom = ClassRoom.objects.create(
            name='Petite Section test',
            section_type=ClassRoom.SectionType.MATERNELLE,
        )
        ChildEnrollment.objects.create(
            child=self.current_child,
            school_year=self.active_year,
            classroom=self.classroom,
        )
        ChildEnrollment.objects.create(
            child=self.previous_child,
            school_year=self.previous_year,
        )

    def test_default_school_year_runs_september_through_june(self):
        self.assertEqual(
            school_year_dates(date(2026, 11, 5)),
            (date(2026, 9, 1), date(2027, 6, 30)),
        )
        self.assertEqual(
            school_year_dates(date(2026, 7, 5)),
            (date(2026, 9, 1), date(2027, 6, 30)),
        )
        next_start, next_end = next_school_year_dates()
        self.assertEqual(next_start.year, self.active_year.start_date.year + 1)
        self.assertEqual(next_start.month, self.active_year.start_date.month)
        self.assertEqual(next_end.year, self.active_year.end_date.year + 1)
        self.assertEqual(next_end.month, self.active_year.end_date.month)

    def test_child_directory_uses_active_year_then_selected_year(self):
        response = self.client.get(reverse('child_list'))
        self.assertContains(response, 'Amina')
        self.assertContains(response, 'Active')
        self.assertNotContains(response, 'Benoit Previous')
        self.assertEqual(
            response.context['selected_school_year'],
            self.active_year,
        )

        response = self.client.post(
            reverse('select_school_year'),
            {
                'school_year': self.previous_year.pk,
                'next': reverse('child_list'),
            },
        )

        self.assertRedirects(response, reverse('child_list'))
        response = self.client.get(reverse('child_list'))
        self.assertContains(response, 'Benoit')
        self.assertContains(response, 'Previous')
        self.assertNotContains(response, 'Amina Active')
        self.assertEqual(
            response.context['selected_school_year'],
            self.previous_year,
        )

    def test_dashboard_classroom_counts_follow_the_selected_year(self):
        response = self.client.get(reverse('dashboard'))
        classroom = response.context['classrooms'].get(pk=self.classroom.pk)
        self.assertEqual(classroom.student_count, 1)

        self.client.post(
            reverse('select_school_year'),
            {
                'school_year': self.previous_year.pk,
                'next': reverse('dashboard'),
            },
        )
        response = self.client.get(reverse('dashboard'))
        classroom = response.context['classrooms'].get(pk=self.classroom.pk)
        self.assertEqual(classroom.student_count, 0)

    def test_new_child_is_enrolled_in_the_selected_year(self):
        self.client.post(
            reverse('select_school_year'),
            {
                'school_year': self.previous_year.pk,
                'next': reverse('child_create'),
            },
        )

        response = self.client.post(
            reverse('child_create'),
            {
                'first_name': 'New',
                'last_name': 'Student',
                'birth_date': '2022-05-04',
                'nationality': 'Burundaise',
                'preferred_hospital': 'Kira Hospital',
                'contacts-TOTAL_FORMS': '1',
                'contacts-INITIAL_FORMS': '0',
                'contacts-MIN_NUM_FORMS': '0',
                'contacts-MAX_NUM_FORMS': '1000',
            },
        )

        self.assertEqual(response.status_code, 302)
        child = Child.objects.get(first_name='New')
        self.assertEqual(
            child.enrollments.get().school_year,
            self.previous_year,
        )

    def test_payment_register_is_filtered_by_selected_school_year(self):
        active_payment = MonthlyFeePayment.objects.create(
            child=self.current_child,
            school_year=self.active_year,
            month='2026-11',
            amount_due=Decimal('50000'),
        )
        previous_payment = MonthlyFeePayment.objects.create(
            child=self.previous_child,
            school_year=self.previous_year,
            month='2026-03',
            amount_due=Decimal('45000'),
        )

        response = self.client.get(reverse('payment_list'))
        self.assertContains(response, active_payment.receipt_number)
        self.assertNotContains(response, previous_payment.receipt_number)

        self.client.post(
            reverse('select_school_year'),
            {
                'school_year': self.previous_year.pk,
                'next': reverse('payment_list'),
            },
        )
        response = self.client.get(reverse('payment_list'))
        self.assertContains(response, previous_payment.receipt_number)
        self.assertNotContains(response, active_payment.receipt_number)

    def test_new_payment_uses_selected_school_year_enrollment(self):
        self.client.post(
            reverse('select_school_year'),
            {
                'school_year': self.previous_year.pk,
                'next': reverse('payment_create'),
            },
        )

        response = self.client.post(
            reverse('payment_create'),
            {
                'child': str(self.previous_child.pk),
                'month': '2026-03',
                'fee_type': MonthlyFeePayment.FeeType.TUITION,
                'amount_due': '45000',
                'amount_paid': '0',
                'late_penalty': '0',
                'status': MonthlyFeePayment.Status.PENDING,
                'payment_date': '',
                'payment_method': '',
                'transaction_reference': 'PREVIOUS-YEAR-TEST',
                'note': '',
            },
        )

        self.assertRedirects(response, reverse('payment_list'))
        payment = MonthlyFeePayment.objects.get(
            transaction_reference='PREVIOUS-YEAR-TEST',
        )
        self.assertEqual(payment.school_year, self.previous_year)
        self.assertEqual(payment.child, self.previous_child)

    def test_year_selector_rejects_external_redirects(self):
        response = self.client.post(
            reverse('select_school_year'),
            {
                'school_year': self.previous_year.pk,
                'next': 'https://example.com/',
            },
        )

        self.assertRedirects(response, reverse('dashboard'))
