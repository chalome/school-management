from uuid import uuid4

from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import F, Q
from django.utils import timezone

from core.models import active_school_year


def generate_receipt_number():
    return f'PEG-REC-{timezone.localdate().year}-{uuid4().hex[:8].upper()}'


class MonthlyFeePayment(models.Model):
    class FeeType(models.TextChoices):
        REGISTRATION = 'registration', 'Inscription'
        MATERIALS = 'materials', 'Matériels'
        UNIFORM = 'uniform', 'Uniforme'
        MINERVAL = 'minerval', 'Minerval'
        OTHER = 'other', 'Autres frais'

        # Keep legacy values readable while existing payment records are retained.
        TUITION = 'tuition', 'Écolage'
        CANTEEN = 'canteen', 'Cantine'
        AFTER_SCHOOL = 'after_school', 'Garderie périscolaire'
        INSURANCE = 'insurance', 'Assurance et carnet'

    class Method(models.TextChoices):
        CASH = 'cash', 'Espèces'
        LUMICASH = 'lumicash', 'Lumicash'
        ECOCASH = 'ecocash', 'EcoCash'
        BANK_TRANSFER = 'bank_transfer', 'Virement bancaire'
        OTHER = 'other', 'Autre'

    class Status(models.TextChoices):
        PAID = 'paid', 'Payé'
        PENDING = 'pending', 'En attente'
        PARTIAL = 'partial', 'Partiellement payé'
        OVERDUE = 'overdue', 'En retard'

    child = models.ForeignKey(
        'children.Child',
        on_delete=models.CASCADE,
        related_name='payments',
    )
    school_year = models.ForeignKey(
        'core.SchoolYear',
        on_delete=models.PROTECT,
        related_name='payments',
        default=active_school_year,
    )
    month = models.CharField(max_length=50)
    fee_type = models.CharField(
        max_length=20,
        choices=FeeType.choices,
        default=FeeType.MINERVAL,
    )
    amount_due = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        help_text='Amount in Fbu',
    )
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Amount in Fbu',
    )
    late_penalty = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        validators=[MinValueValidator(0)],
        help_text='Penalties in Fbu, such as late pickup or late payment fines',
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    payment_date = models.DateField(blank=True, null=True)
    payment_method = models.CharField(
        max_length=20,
        choices=Method.choices,
        blank=True,
    )
    transaction_reference = models.CharField(max_length=100, blank=True)
    note = models.TextField(blank=True)
    proof_of_payment = models.FileField(
        upload_to='payment_proofs/',
        blank=True,
    )
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        default=generate_receipt_number,
        editable=False,
    )

    class Meta:
        ordering = ['-payment_date']
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'month', 'fee_type'],
                name='unique_child_month_fee_type',
            ),
            models.CheckConstraint(
                condition=models.Q(amount_due__gte=0),
                name='payment_amount_due_nonnegative',
            ),
            models.CheckConstraint(
                condition=models.Q(amount_paid__gte=0),
                name='payment_amount_paid_nonnegative',
            ),
            models.CheckConstraint(
                condition=models.Q(late_penalty__gte=0),
                name='payment_late_penalty_nonnegative',
            ),
            models.CheckConstraint(
                condition=Q(amount_paid__lte=F('amount_due') + F('late_penalty')),
                name='payment_amount_paid_not_over_total',
            ),
        ]

    @property
    def total_due(self):
        return self.amount_due + self.late_penalty

    @property
    def balance_due(self):
        return self.total_due - self.amount_paid

    @property
    def enrollment(self):
        return self.child.enrollments.filter(
            school_year=self.school_year,
        ).select_related('classroom').first()

    def __str__(self):
        return f'{self.child} - {self.month} ({self.get_status_display()})'
