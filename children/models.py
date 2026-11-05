from uuid import uuid4

from django.db import models
from django.utils import timezone


def generate_student_number():
    return f'PEG-{timezone.localdate().year}-{uuid4().hex[:6].upper()}'


class Child(models.Model):
    class Sex(models.TextChoices):
        BOY = 'boy', 'Garçon'
        GIRL = 'girl', 'Fille'

    class BloodGroup(models.TextChoices):
        UNKNOWN = '', 'Non renseigné'
        A_POSITIVE = 'A+', 'A+'
        A_NEGATIVE = 'A-', 'A-'
        B_POSITIVE = 'B+', 'B+'
        B_NEGATIVE = 'B-', 'B-'
        AB_POSITIVE = 'AB+', 'AB+'
        AB_NEGATIVE = 'AB-', 'AB-'
        O_POSITIVE = 'O+', 'O+'
        O_NEGATIVE = 'O-', 'O-'

    student_number = models.CharField(
        max_length=20,
        unique=True,
        default=generate_student_number,
        editable=False,
    )
    first_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    sex = models.CharField(max_length=10, choices=Sex.choices, blank=True)
    place_of_birth = models.CharField(max_length=150, blank=True)
    nationality = models.CharField(max_length=50, default='Burundaise')
    spoken_languages = models.CharField(max_length=200, blank=True, null=True)
    is_vaccinated = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='children_photos/', blank=True, null=True)

    father_last_name = models.CharField(max_length=100, blank=True, null=True)
    father_first_name = models.CharField(max_length=100, blank=True, null=True)
    father_profession = models.CharField(max_length=100, blank=True, null=True)
    father_address = models.CharField(max_length=255, blank=True, null=True)
    father_phone = models.CharField(max_length=20, blank=True, null=True)
    father_email = models.EmailField(blank=True, null=True)

    mother_last_name = models.CharField(max_length=100, blank=True, null=True)
    mother_first_name = models.CharField(max_length=100, blank=True, null=True)
    mother_profession = models.CharField(max_length=100, blank=True, null=True)
    mother_address = models.CharField(max_length=255, blank=True, null=True)
    mother_phone = models.CharField(max_length=20, blank=True, null=True)
    mother_email = models.EmailField(blank=True, null=True)

    emergency_contacts = models.TextField(
        blank=True,
        help_text='Legacy notes; use child contacts for structured entries',
    )
    authorized_pickup_persons = models.TextField(
        blank=True,
        help_text='Legacy notes; use child contacts for structured entries',
    )

    blood_group = models.CharField(
        max_length=3,
        choices=BloodGroup.choices,
        blank=True,
    )
    has_health_issues = models.BooleanField(default=False)
    health_issues_details = models.TextField(blank=True, null=True)
    takes_regular_medication = models.BooleanField(default=False)
    medication_details = models.TextField(blank=True, null=True)
    has_allergies = models.BooleanField(default=False)
    allergies_details = models.TextField(blank=True, null=True)
    emergency_medical_instructions = models.TextField(blank=True, null=True)
    preferred_hospital = models.CharField(max_length=150, default='Kira Hospital')

    pediatrician_name = models.CharField(max_length=100, blank=True, null=True)
    pediatrician_address = models.CharField(max_length=255, blank=True, null=True)
    pediatrician_phone = models.CharField(max_length=20, blank=True, null=True)

    registration_date = models.DateField(auto_now_add=True)

    class Meta:
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class ChildContact(models.Model):
    class ContactType(models.TextChoices):
        GUARDIAN = 'guardian', 'Parent / tuteur'
        EMERGENCY = 'emergency', "Contact d'urgence"
        PICKUP = 'pickup', 'Personne autorisée au ramassage'

    child = models.ForeignKey(
        Child,
        on_delete=models.CASCADE,
        related_name='contacts',
    )
    contact_type = models.CharField(max_length=20, choices=ContactType.choices)
    full_name = models.CharField(max_length=150)
    relationship = models.CharField(max_length=80, blank=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['contact_type', 'full_name']

    def __str__(self):
        return f'{self.full_name} ({self.get_contact_type_display()})'
