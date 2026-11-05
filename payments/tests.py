from datetime import date
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from django.urls import reverse

from core.models import ChildEnrollment, SchoolYear
from children.models import Child
from .forms import PaymentForm
from .models import MonthlyFeePayment
from .months import month_label, month_value


class MonthlyFeePaymentModelTests(TestCase):
    def setUp(self):
        self.child = Child.objects.create(
            first_name='Isabelle',
            last_name='Nkurunziza',
            birth_date=date(2022, 4, 12),
            emergency_contacts='Parent: +257 79 00 00 01',
            authorized_pickup_persons='Parent',
        )
        self.school_year = SchoolYear.objects.get(is_active=True)
        ChildEnrollment.objects.create(
            child=self.child,
            school_year=self.school_year,
        )

    def test_total_due_includes_penalty(self):
        payment = MonthlyFeePayment.objects.create(
            child=self.child,
            month='Octobre 2026',
            amount_due=Decimal('50000.00'),
            amount_paid=Decimal('50000.00'),
            late_penalty=Decimal('10000.00'),
            status=MonthlyFeePayment.Status.PAID,
        )

        self.assertEqual(payment.total_due, Decimal('60000.00'))
        self.assertEqual(payment.balance_due, Decimal('10000.00'))
        self.assertTrue(payment.receipt_number.startswith('PEG-REC-'))

    def test_payment_amounts_cannot_be_negative(self):
        payment = MonthlyFeePayment(
            child=self.child,
            month='Octobre 2026',
            amount_due=Decimal('-1.00'),
        )

        with self.assertRaises(ValidationError):
            payment.full_clean()

    def test_paid_amount_cannot_exceed_due_and_penalty(self):
        payment = MonthlyFeePayment(
            child=self.child,
            month='Octobre 2026',
            amount_due=Decimal('50000.00'),
            amount_paid=Decimal('60000.00'),
        )

        with self.assertRaises(ValidationError):
            payment.full_clean()

    def test_payment_screens_require_login_and_render(self):
        self.assertEqual(self.client.get(reverse('payment_list')).status_code, 302)
        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )
        payment = MonthlyFeePayment.objects.create(
            child=self.child,
            month='Octobre 2026',
            amount_due=Decimal('50000.00'),
        )

        self.assertEqual(self.client.get(reverse('payment_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('payment_create')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('payment_detail', args=[payment.pk])).status_code,
            200,
        )

    def test_payment_form_records_fee_and_receipt(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username='accountant',
                password='SecureTestPass123!',
            )
        )
        response = self.client.post(
            reverse('payment_create'),
            {
                'child': str(self.child.pk),
                'month': '2026-11',
                'fee_type': MonthlyFeePayment.FeeType.CANTEEN,
                'amount_due': '80000',
                'amount_paid': '40000',
                'late_penalty': '0',
                'status': MonthlyFeePayment.Status.PARTIAL,
                'payment_date': '2026-11-04',
                'payment_method': MonthlyFeePayment.Method.LUMICASH,
                'transaction_reference': 'LUMI-TEST-2026',
                'note': 'Premier versement',
            },
        )

        payment = MonthlyFeePayment.objects.get(month='2026-11')
        self.assertRedirects(response, reverse('payment_list'))
        self.assertEqual(payment.balance_due, Decimal('40000.00'))
        self.assertTrue(payment.receipt_number)

    def test_month_choices_are_dynamic_and_include_existing_months(self):
        form = PaymentForm()
        choices = dict(form.fields['month'].choices)
        current = timezone.localdate()
        current_value = month_value(current.replace(day=1))
        existing_value = '2019-03'

        payment = MonthlyFeePayment.objects.create(
            child=self.child,
            month=existing_value,
            amount_due=Decimal('50000.00'),
        )
        edit_form = PaymentForm(instance=payment)

        self.assertIsInstance(form.fields['month'].widget, forms.Select)
        self.assertIn(current_value, choices)
        self.assertIn(existing_value, dict(edit_form.fields['month'].choices))
        self.assertEqual(month_label('2026-11'), 'Novembre 2026')

    def test_payment_list_month_filter_uses_exact_month(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username='accountant',
                password='SecureTestPass123!',
            )
        )
        MonthlyFeePayment.objects.create(
            child=self.child,
            month='2026-11',
            amount_due=Decimal('50000.00'),
        )
        MonthlyFeePayment.objects.create(
            child=self.child,
            month='2026-10',
            fee_type=MonthlyFeePayment.FeeType.CANTEEN,
            amount_due=Decimal('10000.00'),
        )

        response = self.client.get(reverse('payment_list'), {'month': '2026-11'})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['payments']), 1)
        self.assertEqual(response.context['payments'][0].month, '2026-11')
