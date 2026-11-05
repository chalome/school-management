from django.contrib import admin
from django.db import transaction

from .models import ChildEnrollment, ClassRoom, SchoolYear


@admin.register(SchoolYear)
class SchoolYearAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'is_active')
    list_filter = ('is_active',)
    ordering = ('-start_date',)

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.is_active:
            return ('is_active',)
        return ()

    def save_model(self, request, obj, form, change):
        with transaction.atomic():
            if obj.is_active:
                SchoolYear.objects.exclude(pk=obj.pk).filter(
                    is_active=True
                ).update(is_active=False)
            super().save_model(request, obj, form, change)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChildEnrollment)
class ChildEnrollmentAdmin(admin.ModelAdmin):
    list_display = ('child', 'school_year', 'classroom', 'attendance_formula')
    list_filter = ('school_year', 'classroom__section_type')
    search_fields = ('child__first_name', 'child__last_name', 'child__student_number')
    list_select_related = ('child', 'school_year', 'classroom')


@admin.register(ClassRoom)
class ClassRoomAdmin(admin.ModelAdmin):
    list_display = ('name', 'section_type', 'teacher')
    list_filter = ('section_type',)
    search_fields = ('name', 'teacher__first_name', 'teacher__last_name')
    list_select_related = ('teacher',)
