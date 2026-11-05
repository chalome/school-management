from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from .forms import TeacherForm
from .models import Teacher


@login_required
def teacher_list(request):
    teachers = Teacher.objects.prefetch_related('classes').all()
    query = request.GET.get('q', '').strip()
    if query:
        teachers = teachers.filter(
            Q(first_name__icontains=query)
            | Q(last_name__icontains=query)
            | Q(employee_number__icontains=query)
            | Q(qualification__icontains=query)
        ).distinct()
    page_obj = Paginator(teachers, 25).get_page(request.GET.get('page'))
    return render(
        request,
        'teachers/teacher_list.html',
        {'teachers': page_obj.object_list, 'page_obj': page_obj, 'query': query},
    )


@login_required
def teacher_detail(request, pk):
    teacher = get_object_or_404(
        Teacher.objects.prefetch_related('classes__children'),
        pk=pk,
    )
    return render(request, 'teachers/teacher_detail.html', {'teacher': teacher})


@login_required
def teacher_create(request):
    return teacher_form(request)


@login_required
def teacher_update(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    return teacher_form(request, teacher)


def teacher_form(request, teacher=None):
    form = TeacherForm(request.POST or None, request.FILES or None, instance=teacher)
    if request.method == 'POST' and form.is_valid():
        saved_teacher = form.save()
        messages.success(request, 'Le dossier de l’enseignant a été enregistré.')
        return redirect('teacher_detail', pk=saved_teacher.pk)
    return render(
        request,
        'teachers/teacher_form.html',
        {'form': form, 'teacher': teacher},
    )
