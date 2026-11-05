from django import forms

from .models import Teacher


class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        exclude = ('user', 'employee_number')
        labels = {
            'title': 'Civilité',
            'first_name': 'Nom & prénoms',
            'last_name': 'Nom de famille',
            'role': 'Fonction / rôle',
            'phone': 'Téléphone direct',
            'email': 'E-mail professionnel',
            'address': 'Adresse',
            'qualification': 'Diplôme principal & établissement',
            'specialty': 'Spécialité',
            'teaching_languages': "Langues d'enseignement",
            'emergency_contact': "Contact d'urgence",
            'has_pediatric_first_aid': 'Premiers secours pédiatriques',
            'has_emergency_plan_training': 'Formation aux protocoles PAI',
            'has_fire_safety_training': 'Formation à la sécurité incendie',
            'medical_clearance': 'Aptitude médicale vérifiée',
            'hire_date': 'Date de prise de fonction',
            'photo': 'Photo',
        }
        widgets = {
            'address': forms.Textarea(attrs={'rows': 2}),
            'emergency_contact': forms.Textarea(attrs={'rows': 2}),
            'hire_date': forms.DateInput(attrs={'type': 'date'}),
        }
