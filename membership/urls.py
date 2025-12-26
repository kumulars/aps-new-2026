"""
APS Membership URL Configuration
"""

from django.urls import path
from . import views

app_name = 'membership'

urlpatterns = [
    path('', views.membership_info, name='info'),
    path('apply/', views.apply_view, name='apply'),
    path('apply/success/', views.apply_success, name='apply_success'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),
    # Status check (magic link)
    path('check-status/', views.status_check_request, name='status_check'),
    path('status/<str:token>/', views.status_check_view, name='status_view'),
]
