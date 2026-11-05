from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render

from core.school_years import get_selected_school_year

from .forms import PaymentForm
from .months import month_choices
from .models import MonthlyFeePayment


@login_required
def payment_list(request):
    school_year = get_selected_school_year(request)
    payments = MonthlyFeePayment.objects.select_related(
        'child',
        'school_year',
    ).filter(school_year=school_year)
    query = request.GET.get('q', '').strip()
    status = request.GET.get('status', '')
    month = request.GET.get('month', '').strip()
    if query:
        payments = payments.filter(
            Q(child__first_name__icontains=query)
            | Q(child__last_name__icontains=query)
            | Q(child__student_number__icontains=query)
            | Q(receipt_number__icontains=query)
            | Q(transaction_reference__icontains=query)
        )
    if status in MonthlyFeePayment.Status.values:
        payments = payments.filter(status=status)
    if month:
        payments = payments.filter(month=month)
    pending_count = payments.filter(
        status__in=[
            MonthlyFeePayment.Status.PENDING,
            MonthlyFeePayment.Status.PARTIAL,
        ]
    ).count()
    overdue_count = payments.filter(status=MonthlyFeePayment.Status.OVERDUE).count()
    filtered_count = payments.count()
    amount_received = payments.aggregate(total=Sum('amount_paid'))['total'] or 0
    page_obj = Paginator(payments, 25).get_page(request.GET.get('page'))
    return render(
        request,
        'payments/payment_list.html',
        {
            'payments': page_obj.object_list,
            'page_obj': page_obj,
            'query': query,
            'selected_status': status,
            'month': month,
            'filtered_count': filtered_count,
            'statuses': MonthlyFeePayment.Status.choices,
            'months': month_choices(
                MonthlyFeePayment.objects.filter(
                    school_year=school_year,
                ).values_list('month', flat=True).distinct()
            ),
            'pending_count': pending_count,
            'overdue_count': overdue_count,
            'amount_received': amount_received,
        },
    )


@login_required
def payment_create(request):
    return payment_form(request)


@login_required
def payment_update(request, pk):
    payment = get_object_or_404(MonthlyFeePayment, pk=pk)
    return payment_form(request, payment)


def payment_form(request, payment=None):
    school_year = payment.school_year if payment else get_selected_school_year(request)
    form = PaymentForm(
        request.POST or None,
        request.FILES or None,
        instance=payment,
        school_year=school_year,
    )
    if request.method == 'POST' and form.is_valid():
        saved_payment = form.save(commit=False)
        saved_payment.school_year = school_year
        saved_payment.save()
        form.save_m2m()
        messages.success(request, 'Le paiement a été enregistré.')
        return redirect('payment_list')
    return render(
        request,
        'payments/payment_form.html',
        {'form': form, 'payment': payment, 'form_school_year': school_year},
    )


@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(
        MonthlyFeePayment.objects.select_related('child', 'school_year'),
        pk=pk,
    )
    return render(request, 'payments/payment_detail.html', {'payment': payment})
