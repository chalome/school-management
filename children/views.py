from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from core.models import ChildEnrollment, ClassRoom
from core.school_years import get_selected_school_year
from .forms import ChildContactFormSet, ChildForm
from .models import Child


@login_required
def child_list(request):
    school_year = get_selected_school_year(request)
    enrollments = ChildEnrollment.objects.filter(
        school_year=school_year,
    ).select_related('child', 'classroom')
    query = request.GET.get('q', '').strip()
    classroom_id = request.GET.get('classroom', '')
    if query:
        enrollments = enrollments.filter(
            Q(child__first_name__icontains=query)
            | Q(child__middle_name__icontains=query)
            | Q(child__last_name__icontains=query)
            | Q(child__student_number__icontains=query)
            | Q(child__father_phone__icontains=query)
            | Q(child__mother_phone__icontains=query)
            | Q(child__contacts__full_name__icontains=query)
            | Q(child__contacts__phone__icontains=query)
        )
        enrollments = enrollments.distinct()
    if classroom_id:
        enrollments = enrollments.filter(classroom_id=classroom_id)
    if request.GET.get('medical') == '1':
        enrollments = enrollments.filter(
            Q(child__has_allergies=True) | Q(child__has_health_issues=True)
        )
    page_obj = Paginator(enrollments, 25).get_page(request.GET.get('page'))
    return render(
        request,
        'children/child_list.html',
        {
            'children': page_obj.object_list,
            'page_obj': page_obj,
            'classrooms': ClassRoom.objects.filter(is_active=True),
            'query': query,
            'selected_classroom': classroom_id,
            'medical_only': request.GET.get('medical') == '1',
        },
    )


@login_required
def child_detail(request, pk):
    school_year = get_selected_school_year(request)
    child = get_object_or_404(
        Child.objects.prefetch_related('contacts'),
        pk=pk,
    )
    enrollment = child.enrollments.filter(
        school_year=school_year,
    ).select_related('classroom').first()
    payments = child.payments.filter(school_year=school_year)
    return render(
        request,
        'children/child_detail.html',
        {'child': child, 'enrollment': enrollment, 'payments': payments},
    )


@login_required
def child_create(request):
    return child_form(request)


@login_required
def child_update(request, pk):
    child = get_object_or_404(Child, pk=pk)
    return child_form(request, child)


def child_form(request, child=None):
    school_year = get_selected_school_year(request)
    form = ChildForm(
        request.POST or None,
        request.FILES or None,
        instance=child,
        school_year=school_year,
    )
    contact_formset = ChildContactFormSet(
        request.POST or None,
        instance=child,
        prefix='contacts',
    )
    if request.method == 'POST' and form.is_valid() and contact_formset.is_valid():
        saved_child = form.save()
        contact_formset.instance = saved_child
        contact_formset.save()
        messages.success(request, 'Le dossier de l’enfant a été enregistré.')
        return redirect('child_detail', pk=saved_child.pk)
    return render(
        request,
        'children/child_form.html',
        {
            'form': form,
            'contact_formset': contact_formset,
            'child': child,
            'school_year': school_year,
        },
    )
