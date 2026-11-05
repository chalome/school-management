from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render, reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from children.models import Child
from payments.models import MonthlyFeePayment
from teachers.models import Teacher

from .forms import ClassRoomForm
from .models import ChildEnrollment, ClassRoom, SchoolYear
from .school_years import SESSION_KEY, get_selected_school_year


@login_required
def dashboard(request):
    school_year = get_selected_school_year(request)
    classrooms = ClassRoom.objects.filter(is_active=True).annotate(
        student_count=Count(
            'enrollments',
            filter=Q(enrollments__school_year=school_year),
        )
    ).select_related('teacher')
    enrolled_children = Child.objects.filter(enrollments__school_year=school_year)
    medical_alerts = ChildEnrollment.objects.filter(
        school_year=school_year,
    ).filter(
        Q(child__has_allergies=True) | Q(child__has_health_issues=True)
    ).select_related('child', 'classroom')
    context = {
        'classrooms': classrooms,
        'total_children': enrolled_children.count(),
        'total_teachers': Teacher.objects.count(),
        'medical_alert_count': enrolled_children.filter(
            Q(has_allergies=True) | Q(has_health_issues=True)
        ).count(),
        'pending_payments': MonthlyFeePayment.objects.filter(
            school_year=school_year,
            status__in=[
                MonthlyFeePayment.Status.PENDING,
                MonthlyFeePayment.Status.PARTIAL,
                MonthlyFeePayment.Status.OVERDUE,
            ]
        ).count(),
        'overdue_payments': MonthlyFeePayment.objects.filter(
            school_year=school_year,
            status=MonthlyFeePayment.Status.OVERDUE
        ).count(),
        'recent_payments': MonthlyFeePayment.objects.select_related(
            'child', 'school_year'
        ).filter(school_year=school_year)[:6],
        'medical_alerts': medical_alerts[:5],
    }
    return render(request, 'core/dashboard.html', context)


@login_required
def classroom_list(request):
    school_year = get_selected_school_year(request)
    classrooms = ClassRoom.objects.annotate(
        student_count=Count(
            'enrollments',
            filter=Q(enrollments__school_year=school_year),
        )
    ).select_related('teacher')
    return render(request, 'core/classroom_list.html', {'classrooms': classrooms})


@login_required
@require_POST
def select_school_year(request):
    year_id = request.POST.get('school_year', '')
    if not year_id.isdecimal():
        raise Http404
    school_year = get_object_or_404(
        SchoolYear,
        pk=int(year_id),
    )
    request.session[SESSION_KEY] = school_year.pk
    next_url = request.POST.get('next', '')
    if not url_has_allowed_host_and_scheme(
        next_url,
        allowed_hosts={request.get_host()},
        require_https=request.is_secure(),
    ):
        next_url = reverse('dashboard')
    return redirect(next_url)


@login_required
def classroom_create(request):
    return classroom_form(request)


@login_required
def classroom_update(request, pk):
    classroom = get_object_or_404(ClassRoom, pk=pk)
    return classroom_form(request, classroom)


def classroom_form(request, classroom=None):
    form = ClassRoomForm(request.POST or None, instance=classroom)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'La salle de classe a été enregistrée.')
        return redirect('classroom_list')
    return render(
        request,
        'core/classroom_form.html',
        {'form': form, 'classroom': classroom},
    )
