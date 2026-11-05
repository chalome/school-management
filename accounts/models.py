from django.db import models

# Create your models here.
from django.conf import settings
from django.db import models


class StaffProfile(models.Model):
    class Unit(models.TextChoices):
        MANAGEMENT = 'management', 'Direction'
        EDUCATION = 'education', 'Éducateurs'
        ACCOUNTING = 'accounting', 'Comptabilité'

    class Language(models.TextChoices):
        FRENCH = 'fr', 'Français'
        KIRUNDI = 'rn', 'Kirundi'
        ENGLISH = 'en', 'English'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='staff_profile',
    )
    unit = models.CharField(
        max_length=20,
        choices=Unit.choices,
        default=Unit.MANAGEMENT,
    )
    title = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    notify_medical_alerts = models.BooleanField(default=True)
    notify_late_pickups = models.BooleanField(default=True)
    notify_payment_followups = models.BooleanField(default=True)
    language = models.CharField(
        max_length=2,
        choices=Language.choices,
        default=Language.FRENCH,
    )

    def __str__(self):
        return f'{self.user.get_full_name() or self.user.username} profile'
