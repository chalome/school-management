from django.contrib import admin

from core.models import ChildEnrollment
from .models import Child, ChildContact


class ChildContactInline(admin.TabularInline):
    model = ChildContact
    extra = 0


class ChildEnrollmentInline(admin.TabularInline):
    model = ChildEnrollment
    extra = 0


@admin.register(Child)
class ChildAdmin(admin.ModelAdmin):
    list_display = (
        'student_number',
        'last_name',
        'first_name',
        'birth_date',
    )
    list_filter = ('is_vaccinated', 'has_allergies')
    search_fields = (
        'student_number',
        'first_name',
        'last_name',
        'father_phone',
        'mother_phone',
    )
    inlines = (ChildContactInline, ChildEnrollmentInline)
