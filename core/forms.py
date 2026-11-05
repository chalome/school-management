from django import forms

from .models import ClassRoom


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ('name', 'section_type', 'teacher', 'capacity', 'is_active')
        labels = {
            'name': 'Nom de la salle',
            'section_type': 'Section',
            'teacher': 'Enseignant référent',
            'capacity': 'Capacité maximale',
            'is_active': 'Salle active',
        }
