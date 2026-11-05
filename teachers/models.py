from uuid import uuid4

from django.conf import settings
from django.db import models
from django.utils import timezone


def generate_employee_number():
    return f'PEG-ENS-{timezone.localdate().year}-{uuid4().hex[:6].upper()}'


class Teacher(models.Model):
    class Title(models.TextChoices):
        MADAME = 'Mme', 'Mme'
        MONSIEUR = 'M.', 'M.'
        DOCTEUR = 'Dr', 'Dr'
        AUTRE = 'Autre', 'Autre'

    class Role(models.TextChoices):
        TEACHER = 'teacher', 'Enseignant(e)'
        ASSISTANT = 'assistant', 'Assistant(e)'
        NURSE = 'nurse', 'Référent(e) médical(e)'
        ADMINISTRATIVE = 'administrative', 'Personnel administratif'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='teacher_record',
        help_text='Optional login account for this teacher',
    )
    employee_number = models.CharField(
        max_length=24,
        unique=True,
        default=generate_employee_number,
        editable=False,
    )
    title = models.CharField(max_length=40, choices=Title.choices, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    role = models.CharField(
        max_length=30,
        choices=Role.choices,
        default=Role.TEACHER,
    )
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    qualification = models.CharField(max_length=200, blank=True)
    specialty = models.CharField(max_length=200, blank=True)
    teaching_languages = models.CharField(max_length=200, blank=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    has_pediatric_first_aid = models.BooleanField(default=False)
    has_emergency_plan_training = models.BooleanField(default=False)
    has_fire_safety_training = models.BooleanField(default=False)
    medical_clearance = models.BooleanField(default=False)
    hire_date = models.DateField(default=timezone.localdate)
    photo = models.ImageField(upload_to='teachers_photos/', blank=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'
