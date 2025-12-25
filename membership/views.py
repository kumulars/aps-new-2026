"""
APS Membership Views

Views for member profile management and membership information.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import MemberProfile
from .forms import ProfileEditForm, MembershipApplicationForm


def membership_info(request):
    """
    Public page displaying membership information and benefits.
    """
    return render(request, 'membership/membership_info.html')


@login_required
def profile_view(request):
    """
    Display the logged-in member's profile.
    Creates a profile if one doesn't exist (for imported users).
    """
    # Get or create profile for the user
    profile, created = MemberProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'status': MemberProfile.STATUS_APPROVED,  # Grandfathered
        }
    )

    if created:
        messages.info(request, "Welcome! Please update your profile information.")

    return render(request, 'membership/profile.html', {
        'profile': profile,
    })


@login_required
def profile_edit(request):
    """
    Edit the logged-in member's profile.
    """
    # Get or create profile for the user
    profile, created = MemberProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'status': MemberProfile.STATUS_APPROVED,
        }
    )

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=profile, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated.")
            return redirect('membership:profile')
    else:
        form = ProfileEditForm(instance=profile, user=request.user)

    return render(request, 'membership/profile_edit.html', {
        'form': form,
        'profile': profile,
    })


def apply_view(request):
    """
    Membership application form for new members.
    Creates User and MemberProfile with pending status.
    """
    # Redirect if already logged in
    if request.user.is_authenticated:
        messages.info(request, "You are already a member.")
        return redirect('membership:profile')

    if request.method == 'POST':
        form = MembershipApplicationForm(request.POST)
        if form.is_valid():
            profile = form.save()
            messages.success(
                request,
                "Thank you for your application! We will review it and contact you soon."
            )
            return redirect('membership:apply_success')
    else:
        form = MembershipApplicationForm()

    return render(request, 'membership/apply.html', {
        'form': form,
    })


def apply_success(request):
    """
    Success page shown after membership application submission.
    """
    return render(request, 'membership/apply_success.html')
