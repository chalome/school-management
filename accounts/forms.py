from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm

from .models import StaffProfile

User = get_user_model()


class UsernameOrEmailAuthenticationForm(AuthenticationForm):
    def clean(self):
        username = self.cleaned_data.get('username', '')
        if '@' in username:
            matches = list(
                User._default_manager.filter(email__iexact=username)
                .order_by('pk')
                .values_list('username', flat=True)[:2]
            )
            if len(matches) == 1:
                self.cleaned_data['username'] = matches[0]
        return super().clean()


class UserDetailsForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        labels = {
            'first_name': 'Prénom',
            'last_name': 'Nom de famille',
            'email': 'Adresse e-mail institutionnelle',
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        duplicates = User._default_manager.filter(email__iexact=email).exclude(
            pk=self.instance.pk
        )
        if email and duplicates.exists():
            raise forms.ValidationError(
                'Cette adresse e-mail est déjà associée à un autre compte.'
            )
        return email


class StaffProfileForm(forms.ModelForm):
    class Meta:
        model = StaffProfile
        fields = (
            'unit',
            'title',
            'phone',
            'language',
            'notify_medical_alerts',
            'notify_late_pickups',
            'notify_payment_followups',
        )
        labels = {
            'unit': "Unité d'activité",
            'title': 'Titre / fonction',
            'phone': 'Téléphone',
            'language': "Langue d'interface",
            'notify_medical_alerts': 'Alertes médicales critiques',
            'notify_late_pickups': 'Retards de ramassage',
            'notify_payment_followups': 'Paiements en attente de suivi',
        }
