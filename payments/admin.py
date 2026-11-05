from django.contrib import admin
from .models import MonthlyFeePayment


@admin.register(MonthlyFeePayment)
class MonthlyFeePaymentAdmin(admin.ModelAdmin):
    list_display = (
        'child',
        'school_year',
        'month',
        'amount_due',
        'amount_paid',
        'late_penalty',
        'fee_type',
        'status',
        'payment_date',
    )
    list_filter = ('school_year', 'status', 'fee_type', 'payment_method', 'month')
    search_fields = (
        'child__first_name',
        'child__last_name',
        'child__student_number',
        'receipt_number',
        'transaction_reference',
    )
    list_select_related = ('child', 'school_year')
