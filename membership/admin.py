from django.contrib import admin
from django.utils import timezone
from django.utils.html import format_html
from .models import MemberProfile


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = [
        'full_name_display',
        'email_display',
        'affiliation_type',
        'membership_type',
        'status_badge',
        'applied_at',
    ]
    list_filter = [
        'status',
        'affiliation_type',
        'membership_type',
        'verification_method',
    ]
    search_fields = [
        'user__first_name',
        'user__last_name',
        'user__email',
        'professional_affiliation',
    ]
    readonly_fields = [
        'applied_at',
        'approved_at',
        'approved_by',
        'created_at',
        'updated_at',
    ]
    actions = ['approve_applications', 'reject_applications']

    fieldsets = (
        ('Member Account', {
            'fields': ('user', 'status')
        }),
        ('Personal Information', {
            'fields': ('title',)
        }),
        ('Address', {
            'fields': (
                'address_1',
                'address_2',
                ('city', 'state_province'),
                ('postal_code', 'country'),
                'phone',
            )
        }),
        ('Professional Information', {
            'fields': (
                'professional_affiliation',
                'affiliation_type',
                'membership_type',
            )
        }),
        ('Verification', {
            'fields': (
                'verification_method',
                'publications',
                ('sponsor_name', 'sponsor_email'),
                'sponsor_letter_received',
            )
        }),
        ('Application Status', {
            'fields': (
                'applied_at',
                'approved_at',
                'approved_by',
                'rejection_reason',
            ),
            'classes': ('collapse',),
        }),
        ('Admin', {
            'fields': ('admin_notes', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    def full_name_display(self, obj):
        return obj.full_name
    full_name_display.short_description = 'Name'

    def email_display(self, obj):
        return obj.user.email
    email_display.short_description = 'Email'

    def status_badge(self, obj):
        colors = {
            'pending': '#f0ad4e',   # Orange
            'approved': '#5cb85c',  # Green
            'rejected': '#d9534f',  # Red
        }
        color = colors.get(obj.status, '#999')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    @admin.action(description='Approve selected applications')
    def approve_applications(self, request, queryset):
        count = 0
        for profile in queryset.filter(status=MemberProfile.STATUS_PENDING):
            profile.approve(request.user)
            count += 1
        self.message_user(request, f'{count} application(s) approved.')

    @admin.action(description='Reject selected applications')
    def reject_applications(self, request, queryset):
        count = queryset.filter(status=MemberProfile.STATUS_PENDING).update(
            status=MemberProfile.STATUS_REJECTED
        )
        self.message_user(request, f'{count} application(s) rejected.')
