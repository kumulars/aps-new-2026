"""
Import members from canonical CSV file.

Usage:
    python manage.py import_members
    python manage.py import_members --dry-run
    python manage.py import_members --limit 10
"""

import csv
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from membership.models import MemberProfile


class Command(BaseCommand):
    help = 'Import members from the canonical member list CSV'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit the number of members to import (for testing)',
        )
        parser.add_argument(
            '--file',
            type=str,
            default='membership/imports/canonical_member_list_final.csv',
            help='Path to the CSV file to import',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options.get('limit')
        csv_file = options['file']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))

        self.stdout.write(f'Reading from: {csv_file}')

        # Track statistics
        stats = {
            'total': 0,
            'created': 0,
            'skipped_exists': 0,
            'skipped_no_email': 0,
            'errors': 0,
        }

        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    stats['total'] += 1

                    if limit and stats['total'] > limit:
                        break

                    email = row.get('email', '').strip()
                    if not email:
                        stats['skipped_no_email'] += 1
                        continue

                    # Check if user already exists
                    if User.objects.filter(email__iexact=email).exists():
                        stats['skipped_exists'] += 1
                        if options['verbosity'] >= 2:
                            self.stdout.write(f'  Skipping (exists): {email}')
                        continue

                    try:
                        if not dry_run:
                            # Create User
                            user = User.objects.create_user(
                                username=email.lower(),
                                email=email,
                                first_name=row.get('mepr_first_name', '')[:150] or '',
                                last_name=row.get('mepr_last_name', '')[:150] or '',
                                # No password - user must reset
                            )

                            # Create MemberProfile
                            profile = MemberProfile.objects.create(
                                user=user,
                                title=row.get('mepr_title', '')[:50] or '',
                                address_1=row.get('mepr_address_1', '')[:255] or '',
                                address_2=row.get('mepr_address_2', '')[:255] or '',
                                city=row.get('mepr_city', '')[:100] or '',
                                state_province=row.get('mepr_state_or_province', '')[:100] or '',
                                postal_code=row.get('mepr_zip_or_postal_code', '')[:20] or '',
                                country=row.get('mepr_country', '')[:100] or '',
                                phone=row.get('mepr_phone', '')[:30] or '',
                                professional_affiliation=row.get('mepr_professional_affiliation', '')[:255] or '',
                                affiliation_type=self._map_affiliation_type(row.get('mepr_affiliation_type', '')),
                                publications=row.get('mepr_publications', '') or '',
                                sponsor_name=row.get('mepr_sponsor', '')[:255] or '',
                                sponsor_email=row.get('mepr_sponsor_email', '')[:254] or '',
                                symposia_attended=row.get('symposia_attended', '')[:100] or '',
                                status=MemberProfile.STATUS_APPROVED,  # Grandfathered
                            )

                        stats['created'] += 1
                        if options['verbosity'] >= 2:
                            self.stdout.write(self.style.SUCCESS(f'  Created: {email}'))

                    except Exception as e:
                        stats['errors'] += 1
                        self.stdout.write(self.style.ERROR(f'  Error for {email}: {str(e)}'))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_file}'))
            return

        # Print summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('Import Summary'))
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(f'Total rows processed: {stats["total"]}')
        self.stdout.write(self.style.SUCCESS(f'Created: {stats["created"]}'))
        self.stdout.write(f'Skipped (already exists): {stats["skipped_exists"]}')
        self.stdout.write(f'Skipped (no email): {stats["skipped_no_email"]}')
        if stats['errors']:
            self.stdout.write(self.style.ERROR(f'Errors: {stats["errors"]}'))

        if dry_run:
            self.stdout.write('')
            self.stdout.write(self.style.WARNING('DRY RUN - No changes were made'))

    def _map_affiliation_type(self, value):
        """Map CSV affiliation type to model choice."""
        value = (value or '').lower().strip()

        mapping = {
            'academic': MemberProfile.AFFILIATION_ACADEMIC,
            'government': MemberProfile.AFFILIATION_GOVERNMENT,
            'industry': MemberProfile.AFFILIATION_INDUSTRY,
            'nonprofit': MemberProfile.AFFILIATION_NONPROFIT,
            'non-profit': MemberProfile.AFFILIATION_NONPROFIT,
            'other': MemberProfile.AFFILIATION_OTHER,
        }

        return mapping.get(value, MemberProfile.AFFILIATION_OTHER)
