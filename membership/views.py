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


# =============================================================================
# MEMBERSHIP STATUS CHECK (Magic Link)
# =============================================================================

def status_check_request(request):
    """
    Form to request a membership status check.
    User enters email, we send a magic link.
    """
    from django.core.mail import send_mail
    from django.conf import settings
    from django.contrib.auth.models import User
    from .models import MembershipStatusToken

    email_sent = False

    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()

        if email:
            # Always show success message (don't reveal if email exists)
            email_sent = True

            # Check if user with this email exists
            try:
                user = User.objects.get(email__iexact=email)

                # Create magic link token
                token_obj = MembershipStatusToken.create_for_email(email)

                # Build the magic link URL
                magic_link = request.build_absolute_uri(
                    f'/membership/status/{token_obj.token}/'
                )

                # Send email
                send_mail(
                    subject='Your APS Membership Status',
                    message=f'''Hello,

You requested to check your membership status with the American Peptide Society.

Click the link below to view your membership status:
{magic_link}

This link will expire in 24 hours.

If you did not request this, you can safely ignore this email.

Best regards,
American Peptide Society
''',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
            except User.DoesNotExist:
                # Don't reveal that email doesn't exist
                pass

    return render(request, 'membership/status_check_request.html', {
        'email_sent': email_sent,
    })


def status_check_view(request, token):
    """
    Display membership status for a valid magic link token.
    """
    from django.contrib.auth.models import User
    from .models import MembershipStatusToken

    try:
        token_obj = MembershipStatusToken.objects.get(token=token)
    except MembershipStatusToken.DoesNotExist:
        return render(request, 'membership/status_check_invalid.html', {
            'reason': 'invalid',
        })

    if token_obj.is_expired:
        return render(request, 'membership/status_check_invalid.html', {
            'reason': 'expired',
        })

    # Mark token as used (optional - allow multiple views within 24h)
    # token_obj.mark_used()

    # Find the user and their profile
    try:
        user = User.objects.get(email__iexact=token_obj.email)
        profile = getattr(user, 'member_profile', None)
    except User.DoesNotExist:
        return render(request, 'membership/status_check_invalid.html', {
            'reason': 'not_found',
        })

    return render(request, 'membership/status_check_result.html', {
        'user': user,
        'profile': profile,
    })
