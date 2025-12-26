"""
APS Membership Models

This module defines the membership system for the American Peptide Society.
Uses django-allauth for authentication, with a custom MemberProfile for
additional member data.
"""

import secrets
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from wagtail.images.models import Image


class MemberProfile(models.Model):
    """
    Extended profile for APS members.
    Links to Django's User model via OneToOne relationship.
    """

    # === Affiliation Type Choices ===
    AFFILIATION_ACADEMIC = 'academic'
    AFFILIATION_GOVERNMENT = 'government'
    AFFILIATION_INDUSTRY = 'industry'
    AFFILIATION_NONPROFIT = 'nonprofit'
    AFFILIATION_OTHER = 'other'

    AFFILIATION_CHOICES = [
        (AFFILIATION_ACADEMIC, 'Academic'),
        (AFFILIATION_GOVERNMENT, 'Government'),
        (AFFILIATION_INDUSTRY, 'Industry'),
        (AFFILIATION_NONPROFIT, 'Non-Profit'),
        (AFFILIATION_OTHER, 'Other'),
    ]

    # === Membership Type Choices ===
    MEMBERSHIP_PROFESSIONAL = 'professional'
    MEMBERSHIP_RETIRED = 'retired'
    MEMBERSHIP_POSTDOC = 'postdoc'
    MEMBERSHIP_STUDENT = 'student'

    MEMBERSHIP_CHOICES = [
        (MEMBERSHIP_PROFESSIONAL, 'Professional'),
        (MEMBERSHIP_RETIRED, 'Retired Professional'),
        (MEMBERSHIP_POSTDOC, 'Postdoc'),
        (MEMBERSHIP_STUDENT, 'Student'),
    ]

    # === Application Status Choices ===
    STATUS_PENDING = 'pending'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Review'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_REJECTED, 'Rejected'),
    ]

    # === Verification Method Choices ===
    VERIFICATION_PUBLICATIONS = 'publications'
    VERIFICATION_SPONSOR = 'sponsor'

    VERIFICATION_CHOICES = [
        (VERIFICATION_PUBLICATIONS, 'Has published in peptide science'),
        (VERIFICATION_SPONSOR, 'Will provide sponsor reference'),
    ]

    # -------------------------------------------------------------------------
    # Core Link to User
    # -------------------------------------------------------------------------
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='member_profile'
    )

    # -------------------------------------------------------------------------
    # Personal Information
    # -------------------------------------------------------------------------
    title = models.CharField(
        max_length=50,
        blank=True,
        help_text="e.g., Dr., Professor, Ph.D."
    )
    # Note: first_name and last_name are on the User model

    # -------------------------------------------------------------------------
    # Address (all optional to grandfather imported members)
    # -------------------------------------------------------------------------
    address_1 = models.CharField(max_length=255, blank=True)
    address_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state_province = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="State or Province"
    )
    postal_code = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="ZIP or Postal Code"
    )
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=30, blank=True)

    # -------------------------------------------------------------------------
    # Professional Information (optional to grandfather imported members)
    # -------------------------------------------------------------------------
    professional_affiliation = models.CharField(
        max_length=255,
        blank=True,
        help_text="Institution or organization name"
    )
    affiliation_type = models.CharField(
        max_length=20,
        choices=AFFILIATION_CHOICES,
        default=AFFILIATION_ACADEMIC
    )
    membership_type = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_CHOICES,
        default=MEMBERSHIP_PROFESSIONAL
    )

    # -------------------------------------------------------------------------
    # Verification (Publications OR Sponsor)
    # -------------------------------------------------------------------------
    verification_method = models.CharField(
        max_length=20,
        choices=VERIFICATION_CHOICES,
        default=VERIFICATION_PUBLICATIONS,
        help_text="How the applicant verifies their involvement in peptide science"
    )

    # If verification_method == 'publications'
    publications = models.TextField(
        blank=True,
        help_text="List of publications (citations or DOIs)"
    )

    # If verification_method == 'sponsor'
    sponsor_name = models.CharField(max_length=255, blank=True)
    sponsor_email = models.EmailField(blank=True)
    sponsor_letter_received = models.BooleanField(
        default=False,
        help_text="Check when sponsor letter has been received"
    )

    # -------------------------------------------------------------------------
    # Application Status & Tracking
    # -------------------------------------------------------------------------
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )
    applied_at = models.DateTimeField(default=timezone.now)
    approved_at = models.DateTimeField(null=True, blank=True)
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_members',
        help_text="Admin who approved this application"
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection, if applicable"
    )

    # -------------------------------------------------------------------------
    # Admin Notes
    # -------------------------------------------------------------------------
    admin_notes = models.TextField(
        blank=True,
        help_text="Internal notes (not visible to member)"
    )

    # -------------------------------------------------------------------------
    # Symposia Attendance
    # -------------------------------------------------------------------------
    symposia_attended = models.CharField(
        max_length=100,
        blank=True,
        help_text="Comma-separated list of symposium years attended (e.g., '2019,2022,2025')"
    )

    # -------------------------------------------------------------------------
    # Profile Image (optional)
    # -------------------------------------------------------------------------
    profile_image = models.ForeignKey(
        Image,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_profiles',
        help_text="Optional profile photo"
    )

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Member Profile"
        verbose_name_plural = "Member Profiles"
        ordering = ['-applied_at']

    def __str__(self):
        return f"{self.user.get_full_name()} ({self.user.email})"

    @property
    def full_name(self):
        """Returns formatted full name with title."""
        if self.title:
            return f"{self.title} {self.user.first_name} {self.user.last_name}"
        return self.user.get_full_name()

    @property
    def is_approved(self):
        return self.status == self.STATUS_APPROVED

    @property
    def is_pending(self):
        return self.status == self.STATUS_PENDING

    def approve(self, approved_by_user):
        """Approve the membership application."""
        self.status = self.STATUS_APPROVED
        self.approved_at = timezone.now()
        self.approved_by = approved_by_user
        self.save()

    def reject(self, reason=''):
        """Reject the membership application."""
        self.status = self.STATUS_REJECTED
        self.rejection_reason = reason
        self.save()


class MembershipStatusToken(models.Model):
    """
    Secure token for magic link membership status checks.
    Tokens expire after 24 hours for security.
    """
    email = models.EmailField()
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Status Check Token"
        verbose_name_plural = "Status Check Tokens"

    def __str__(self):
        return f"Token for {self.email} ({self.created_at})"

    @classmethod
    def create_for_email(cls, email):
        """Create a new token for the given email."""
        token = secrets.token_urlsafe(32)
        return cls.objects.create(email=email.lower(), token=token)

    @property
    def is_expired(self):
        """Token expires 24 hours after creation."""
        return timezone.now() > self.created_at + timedelta(hours=24)

    @property
    def is_valid(self):
        """Token is valid if not expired and not yet used."""
        return not self.is_expired and self.used_at is None

    def mark_used(self):
        """Mark token as used."""
        self.used_at = timezone.now()
        self.save()
