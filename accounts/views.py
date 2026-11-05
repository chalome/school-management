from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import redirect, render

from .forms import StaffProfileForm, UserDetailsForm
from .models import StaffProfile


@login_required
def profile(request):
    profile, _ = StaffProfile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user_form = UserDetailsForm(request.POST, instance=request.user)
        profile_form = StaffProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            with transaction.atomic():
                user_form.save()
                profile_form.save()
            messages.success(request, 'Votre profil a été mis à jour.')
            return redirect('profile')
    else:
        user_form = UserDetailsForm(instance=request.user)
        profile_form = StaffProfileForm(instance=profile)
    return render(
        request,
        'accounts/profile.html',
        {'user_form': user_form, 'profile_form': profile_form},
    )
