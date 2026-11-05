from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import StaffProfile


class AuthenticationUrlTests(TestCase):
    def test_login_page_is_available(self):
        response = self.client.get(reverse('login'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '/static/logo.png')
        self.assertContains(response, '/static/logo.ico')

    def test_staff_can_sign_in_with_unique_email(self):
        user = get_user_model().objects.create_user(
            username='director',
            email='director@example.bi',
            password='SecureTestPass123!',
        )

        response = self.client.post(
            reverse('login'),
            {'username': user.email, 'password': 'SecureTestPass123!'},
        )

        self.assertRedirects(response, reverse('dashboard'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_profile_requires_authentication_and_can_be_updated(self):
        response = self.client.get(reverse('profile'))
        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("profile")}',
        )

        user = get_user_model().objects.create_user(
            username='clotilde',
            password='SecureTestPass123!',
        )
        self.client.force_login(user)
        response = self.client.post(
            reverse('profile'),
            {
                'first_name': 'Clotilde',
                'last_name': 'Nizigiyimana',
                'email': 'clotilde@example.bi',
                'unit': StaffProfile.Unit.MANAGEMENT,
                'title': 'Direction',
                'phone': '+257 79 00 00 00',
                'language': StaffProfile.Language.FRENCH,
            },
        )

        self.assertRedirects(response, reverse('profile'))
        user.refresh_from_db()
        self.assertEqual(user.first_name, 'Clotilde')
        self.assertEqual(user.staff_profile.phone, '+257 79 00 00 00')
