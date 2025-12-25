"""
APS Membership Forms

Forms for member profile management and membership applications.
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import MemberProfile


class ProfileEditForm(forms.ModelForm):
    """
    Form for members to edit their own profile.
    Excludes admin-only fields and status fields.
    """

    # Include first_name and last_name from User model
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )

    class Meta:
        model = MemberProfile
        fields = [
            'title',
            'phone',
            'professional_affiliation',
            'affiliation_type',
            'address_1',
            'address_2',
            'city',
            'state_province',
            'postal_code',
            'country',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Dr., Professor, Ph.D.'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'professional_affiliation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Institution or Organization'
            }),
            'affiliation_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address'
            }),
            'address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apt, Suite, Building (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State or Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP or Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
        }

    def __init__(self, *args, **kwargs):
        """Pre-populate first_name and last_name from the User model."""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            self.fields['first_name'].initial = self.user.first_name
            self.fields['last_name'].initial = self.user.last_name

    def save(self, commit=True):
        """Save both User and MemberProfile data."""
        profile = super().save(commit=False)

        if self.user:
            self.user.first_name = self.cleaned_data['first_name']
            self.user.last_name = self.cleaned_data['last_name']
            if commit:
                self.user.save()

        if commit:
            profile.save()

        return profile


class MembershipApplicationForm(forms.ModelForm):
    """
    Form for new membership applications.
    Creates both User and MemberProfile on submission.
    """

    # User fields
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'you@example.com'
        })
    )
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'First Name'
        })
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Last Name'
        })
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a password'
        })
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    )

    class Meta:
        model = MemberProfile
        fields = [
            'title',
            'phone',
            'professional_affiliation',
            'affiliation_type',
            'membership_type',
            'address_1',
            'address_2',
            'city',
            'state_province',
            'postal_code',
            'country',
            'verification_method',
            'publications',
            'sponsor_name',
            'sponsor_email',
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Dr., Professor, Ph.D.'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'professional_affiliation': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'University, Company, or Organization'
            }),
            'affiliation_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'membership_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'address_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Street Address'
            }),
            'address_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Apt, Suite, Building (optional)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'state_province': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State or Province'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP or Postal Code'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Country'
            }),
            'verification_method': forms.RadioSelect(attrs={
                'class': 'form-check-input'
            }),
            'publications': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'List your peptide-related publications (citations or DOIs)'
            }),
            'sponsor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sponsor\'s full name'
            }),
            'sponsor_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Sponsor\'s email address'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make professional_affiliation required for applications
        self.fields['professional_affiliation'].required = True

    def clean_email(self):
        """Ensure email is unique."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('An account with this email already exists. Please login instead.')
        return email.lower()

    def clean(self):
        """Validate password match and verification requirements."""
        cleaned_data = super().clean()

        # Check passwords match
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')

        # Check verification method requirements
        verification_method = cleaned_data.get('verification_method')
        if verification_method == MemberProfile.VERIFICATION_PUBLICATIONS:
            publications = cleaned_data.get('publications', '').strip()
            if not publications:
                self.add_error('publications', 'Please provide your publications.')
        elif verification_method == MemberProfile.VERIFICATION_SPONSOR:
            sponsor_name = cleaned_data.get('sponsor_name', '').strip()
            sponsor_email = cleaned_data.get('sponsor_email', '').strip()
            if not sponsor_name:
                self.add_error('sponsor_name', 'Please provide your sponsor\'s name.')
            if not sponsor_email:
                self.add_error('sponsor_email', 'Please provide your sponsor\'s email.')

        return cleaned_data

    def save(self, commit=True):
        """Create User and MemberProfile."""
        # Create User
        user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
        )

        # Create MemberProfile
        profile = super().save(commit=False)
        profile.user = user
        profile.status = MemberProfile.STATUS_PENDING  # Requires admin approval

        if commit:
            profile.save()

        return profile
