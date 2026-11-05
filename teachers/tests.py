from django import forms
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .forms import TeacherForm
from .models import Teacher


class TeacherModelTests(TestCase):
    def test_title_is_a_select_with_civility_choices(self):
        form = TeacherForm()

        self.assertIsInstance(form.fields['title'].widget, forms.Select)
        self.assertIn(('Mme', 'Mme'), form.fields['title'].choices)

    def test_teacher_string_representation(self):
        teacher = Teacher.objects.create(
            first_name='Aline',
            last_name='Niyonzima',
            phone='+257 79 00 00 00',
        )

        self.assertEqual(str(teacher), 'Aline Niyonzima')
        self.assertTrue(teacher.employee_number.startswith('PEG-ENS-'))

    def test_teacher_pages_require_login_and_render(self):
        self.assertEqual(self.client.get(reverse('teacher_list')).status_code, 302)
        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )
        teacher = Teacher.objects.create(
            first_name='Aline',
            last_name='Niyonzima',
            phone='+257 79 00 00 00',
        )

        self.assertEqual(self.client.get(reverse('teacher_list')).status_code, 200)
        self.assertEqual(self.client.get(reverse('teacher_create')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('teacher_detail', args=[teacher.pk])).status_code,
            200,
        )

    def test_teacher_form_creates_staff_record(self):
        self.client.force_login(
            get_user_model().objects.create_user(
                username='admin',
                password='SecureTestPass123!',
            )
        )
        response = self.client.post(
            reverse('teacher_create'),
            {
                'first_name': 'Chantal',
                'last_name': 'Nizigama',
                'role': Teacher.Role.TEACHER,
                'phone': '+257 79 00 00 02',
                'hire_date': '2025-02-01',
            },
        )

        teacher = Teacher.objects.get(first_name='Chantal')
        self.assertRedirects(response, reverse('teacher_detail', args=[teacher.pk]))
        self.assertEqual(teacher.hire_date.isoformat(), '2025-02-01')
