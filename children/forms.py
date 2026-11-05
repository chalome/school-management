from django import forms
from django.forms import inlineformset_factory

from core.models import ChildEnrollment, ClassRoom, active_school_year

from .models import Child, ChildContact


class ChildForm(forms.ModelForm):
    classroom = forms.ModelChoiceField(
        queryset=ClassRoom.objects.all(),
        required=False,
        label='Classe',
    )
    attendance_formula = forms.ChoiceField(
        choices=[('', '---------'), *ChildEnrollment.AttendanceFormula.choices],
        required=False,
        label="Formule d'accueil",
    )

    class Meta:
        model = Child
        exclude = (
            'student_number',
            'registration_date',
            'emergency_contacts',
            'authorized_pickup_persons',
            'classroom',
            'attendance_formula',
        )
        labels = {
            'first_name': "Prénom de l'enfant",
            'middle_name': 'Post-nom',
            'last_name': 'Nom de famille',
            'birth_date': 'Date de naissance',
            'sex': 'Sexe',
            'place_of_birth': 'Lieu de naissance',
            'nationality': 'Nationalité',
            'spoken_languages': 'Langues parlées',
            'is_vaccinated': 'Vaccinations à jour',
            'classroom': 'Classe',
            'attendance_formula': "Formule d'accueil",
            'father_first_name': 'Prénom du père / tuteur 1',
            'father_last_name': 'Nom du père / tuteur 1',
            'father_profession': 'Profession du père / tuteur 1',
            'father_address': 'Adresse du père / tuteur 1',
            'father_phone': 'Téléphone du père / tuteur 1',
            'father_email': 'E-mail du père / tuteur 1',
            'mother_first_name': 'Prénom de la mère / tuteur 2',
            'mother_last_name': 'Nom de la mère / tuteur 2',
            'mother_profession': 'Profession de la mère / tuteur 2',
            'mother_address': 'Adresse de la mère / tuteur 2',
            'mother_phone': 'Téléphone de la mère / tuteur 2',
            'mother_email': 'E-mail de la mère / tuteur 2',
            'blood_group': 'Groupe sanguin',
            'has_health_issues': 'Antécédents de santé',
            'health_issues_details': 'Détails des antécédents',
            'takes_regular_medication': 'Traitement régulier',
            'medication_details': 'Détails du traitement',
            'has_allergies': 'Allergies connues',
            'allergies_details': 'Allergènes identifiés',
            'emergency_medical_instructions': "Protocole d'urgence",
            'preferred_hospital': 'Hôpital préféré',
            'pediatrician_name': 'Nom du pédiatre',
            'pediatrician_address': 'Adresse du pédiatre',
            'pediatrician_phone': 'Téléphone du pédiatre',
            'photo': 'Photo de l’enfant',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'health_issues_details': forms.Textarea(attrs={'rows': 3}),
            'medication_details': forms.Textarea(attrs={'rows': 3}),
            'allergies_details': forms.Textarea(attrs={'rows': 3}),
            'emergency_medical_instructions': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, school_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.school_year = school_year or active_school_year()
        if self.instance.pk:
            enrollment = self.instance.enrollments.filter(
                school_year=self.school_year,
            ).first()
            if enrollment:
                self.initial['classroom'] = enrollment.classroom_id
                self.initial['attendance_formula'] = enrollment.attendance_formula

    def save(self, commit=True):
        child = super().save(commit=commit)
        if commit:
            ChildEnrollment.objects.update_or_create(
                child=child,
                school_year=self.school_year,
                defaults={
                    'classroom': self.cleaned_data['classroom'],
                    'attendance_formula': self.cleaned_data['attendance_formula'],
                },
            )
        return child


class ChildContactForm(forms.ModelForm):
    class Meta:
        model = ChildContact
        fields = (
            'contact_type',
            'full_name',
            'relationship',
            'phone',
            'email',
            'address',
            'is_primary',
            'notes',
        )
        labels = {
            'contact_type': 'Type de contact',
            'full_name': 'Nom complet',
            'relationship': 'Lien avec l’enfant',
            'phone': 'Téléphone',
            'email': 'E-mail',
            'address': 'Adresse',
            'is_primary': 'Contact principal',
            'notes': 'Note',
        }
        widgets = {'notes': forms.Textarea(attrs={'rows': 2})}


ChildContactFormSet = inlineformset_factory(
    Child,
    ChildContact,
    form=ChildContactForm,
    extra=1,
    can_delete=True,
)
