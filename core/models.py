from calendar import monthrange
from datetime import date

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.utils import timezone


DEFAULT_SCHOOL_YEAR_START_MONTH = 9
DEFAULT_SCHOOL_YEAR_END_MONTH = 6


def school_year_dates(today=None):
    today = today or timezone.localdate()
    start_year = today.year
    if DEFAULT_SCHOOL_YEAR_END_MONTH < DEFAULT_SCHOOL_YEAR_START_MONTH:
        if not (
            today.month >= DEFAULT_SCHOOL_YEAR_START_MONTH
            or today.month > DEFAULT_SCHOOL_YEAR_END_MONTH
        ):
            start_year -= 1
    elif today.month < DEFAULT_SCHOOL_YEAR_START_MONTH:
        start_year -= 1
    end_year = start_year
    if DEFAULT_SCHOOL_YEAR_END_MONTH < DEFAULT_SCHOOL_YEAR_START_MONTH:
        end_year += 1
    return (
        date(start_year, DEFAULT_SCHOOL_YEAR_START_MONTH, 1),
        date(
            end_year,
            DEFAULT_SCHOOL_YEAR_END_MONTH,
            monthrange(end_year, DEFAULT_SCHOOL_YEAR_END_MONTH)[1],
        ),
    )


def default_school_year_start():
    return next_school_year_dates()[0]


def default_school_year_end():
    return next_school_year_dates()[1]


def next_school_year_dates():
    current_year = SchoolYear.objects.filter(is_active=True).first()
    if current_year is None:
        return school_year_dates()

    next_start_year = current_year.start_date.year + 1
    next_end_year = current_year.end_date.year + 1
    start_day = min(
        current_year.start_date.day,
        monthrange(next_start_year, current_year.start_date.month)[1],
    )
    end_day = min(
        current_year.end_date.day,
        monthrange(next_end_year, current_year.end_date.month)[1],
    )
    return (
        date(next_start_year, current_year.start_date.month, start_day),
        date(next_end_year, current_year.end_date.month, end_day),
    )


def active_school_year():
    return SchoolYear.objects.get(is_active=True)


class SchoolYear(models.Model):
    start_date = models.DateField(default=default_school_year_start)
    end_date = models.DateField(default=default_school_year_end)
    is_active = models.BooleanField(default=False)

    class Meta:
        ordering = ['-start_date']
        constraints = [
            models.CheckConstraint(
                condition=Q(end_date__gt=models.F('start_date')),
                name='school_year_end_after_start',
            ),
            models.UniqueConstraint(
                fields=['is_active'],
                condition=Q(is_active=True),
                name='only_one_active_school_year',
            ),
            models.UniqueConstraint(
                fields=['start_date', 'end_date'],
                name='unique_school_year_date_range',
            ),
        ]

    def clean(self):
        super().clean()
        if self.end_date and self.start_date and self.end_date <= self.start_date:
            raise ValidationError({'end_date': 'La fin doit être après le début.'})
        if self.start_date and self.end_date:
            overlapping_years = SchoolYear.objects.exclude(pk=self.pk).filter(
                start_date__lte=self.end_date,
                end_date__gte=self.start_date,
            )
            if overlapping_years.exists():
                raise ValidationError(
                    'Les dates chevauchent une autre année scolaire.'
                )

    @property
    def name(self):
        if self.start_date.year == self.end_date.year:
            return str(self.start_date.year)
        return f'{self.start_date.year}-{self.end_date.year}'

    def __str__(self):
        return self.name


class ChildEnrollment(models.Model):
    class AttendanceFormula(models.TextChoices):
        MORNING = 'morning', 'Matinée simple'
        FULL_DAY = 'full_day', 'Journée complète avec déjeuner'

    child = models.ForeignKey(
        'children.Child',
        on_delete=models.CASCADE,
        related_name='enrollments',
    )
    school_year = models.ForeignKey(
        SchoolYear,
        on_delete=models.PROTECT,
        related_name='enrollments',
    )
    classroom = models.ForeignKey(
        'core.ClassRoom',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='enrollments',
    )
    attendance_formula = models.CharField(
        max_length=20,
        choices=AttendanceFormula.choices,
        blank=True,
    )

    class Meta:
        ordering = ['child__last_name', 'child__first_name']
        constraints = [
            models.UniqueConstraint(
                fields=['child', 'school_year'],
                name='unique_child_enrollment_per_year',
            ),
        ]

    def __str__(self):
        return f'{self.child} — {self.school_year}'


class ClassRoom(models.Model):
    class SectionType(models.TextChoices):
        CRECHE = 'creche', 'Crèche'
        MATERNELLE = 'maternelle', 'Maternelle'

    name = models.CharField(max_length=100)
    section_type = models.CharField(max_length=20, choices=SectionType.choices)
    capacity = models.PositiveSmallIntegerField(default=30)
    is_active = models.BooleanField(default=True)
    teacher = models.ForeignKey(
        'teachers.Teacher',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='classes',
    )

    class Meta:
        ordering = ['section_type', 'name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'section_type'],
                name='unique_classroom_name_per_section',
            ),
        ]

    def __str__(self):
        return f'{self.name} ({self.get_section_type_display()})'
