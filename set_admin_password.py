#!/usr/bin/env python
"""
Simple script to set admin password
Run with: python set_admin_password.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aps_site.settings.dev')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Create or update the superuser
try:
    user = User.objects.get(username='larsaps2026')
    user.set_password('QbxkQlMnA3fbRsfS57xud')
    user.is_superuser = True
    user.is_staff = True
    user.save()
    print("Password updated for existing user 'larsaps2026'")
except User.DoesNotExist:
    user = User.objects.create_superuser(
        username='larsaps2026',
        email='lars@aps.local',
        password='QbxkQlMnA3fbRsfS57xud'
    )
    print("New superuser 'larsaps2026' created successfully")

print("Username: larsaps2026")
print("Password: QbxkQlMnA3fbRsfS57xud")
print("\nYou can now login at http://localhost:8000/admin")
