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
]
