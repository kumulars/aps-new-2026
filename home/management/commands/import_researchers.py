"""
Import researchers from old aps2026 project.

Reads from /Users/larssahl/documents/wagtail/aps2026/db.sqlite3
and imports into the new site.
"""

import sqlite3
from pathlib import Path

from django.core.management.base import BaseCommand
from django.utils.text import slugify

from home.models import Researcher, ResearchArea


class Command(BaseCommand):
    help = 'Import researchers from old aps2026 project'

    OLD_DB_PATH = Path('/Users/larssahl/documents/wagtail/aps2026/db.sqlite3')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing data before importing',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        clear = options['clear']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))

        if not self.OLD_DB_PATH.exists():
            self.stdout.write(self.style.ERROR(f'Database not found: {self.OLD_DB_PATH}'))
            return

        # Connect to old database
        conn = sqlite3.connect(self.OLD_DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if clear and not dry_run:
            self.stdout.write('Clearing existing data...')
            Researcher.objects.all().delete()
            ResearchArea.objects.all().delete()
            self.stdout.write(self.style.SUCCESS('Cleared existing data'))

        # Step 1: Import Research Areas
        self.stdout.write('\n=== Importing Research Areas ===')
        cursor.execute('SELECT id, name, description, slug FROM home_researcharea ORDER BY name')
        old_areas = cursor.fetchall()

        area_mapping = {}  # old_id -> new_id
        areas_created = 0

        for row in old_areas:
            old_id = row['id']
            name = row['name']
            description = row['description'] or ''
            slug = row['slug'] or slugify(name)

            if dry_run:
                self.stdout.write(f'  Would import: {name}')
                areas_created += 1
                continue

            # Check if exists
            existing = ResearchArea.objects.filter(name=name).first()
            if existing:
                area_mapping[old_id] = existing.id
                self.stdout.write(f'  Exists: {name}')
            else:
                area = ResearchArea.objects.create(
                    name=name,
                    description=description,
                    slug=slug
                )
                area_mapping[old_id] = area.id
                areas_created += 1
                self.stdout.write(self.style.SUCCESS(f'  Created: {name}'))

        self.stdout.write(f'Research areas: {areas_created} created')

        # Step 2: Import Researchers
        self.stdout.write('\n=== Importing Researchers ===')
        cursor.execute('''
            SELECT
                id, first_name, last_name, title,
                institution, department,
                country, state_province, city,
                website_url, orcid_id, pubmed_url, google_scholar_url,
                research_keywords, is_active
            FROM home_researcher
            WHERE is_active = 1
            ORDER BY last_name, first_name
        ''')
        old_researchers = cursor.fetchall()

        researchers_created = 0
        researchers_skipped = 0

        for row in old_researchers:
            old_id = row['id']
            first_name = row['first_name']
            last_name = row['last_name']

            if dry_run:
                self.stdout.write(f'  Would import: {last_name}, {first_name}')
                researchers_created += 1
                continue

            # Check if exists
            existing = Researcher.objects.filter(
                first_name=first_name,
                last_name=last_name,
                institution=row['institution']
            ).first()

            if existing:
                researchers_skipped += 1
                continue

            # Create researcher
            researcher = Researcher.objects.create(
                first_name=first_name,
                last_name=last_name,
                title=row['title'] or '',
                institution=row['institution'],
                department=row['department'] or '',
                country=row['country'] or 'USA',
                state_province=row['state_province'] or '',
                city=row['city'] or '',
                website_url=row['website_url'] or '',
                orcid_id=row['orcid_id'] or '',
                pubmed_url=row['pubmed_url'] or '',
                google_scholar_url=row['google_scholar_url'] or '',
                research_keywords=row['research_keywords'] or '',
                is_active=True
            )

            # Get research area relationships
            cursor.execute('''
                SELECT researcharea_id
                FROM home_researcher_research_areas
                WHERE researcher_id = ?
            ''', (old_id,))
            area_ids = cursor.fetchall()

            for area_row in area_ids:
                old_area_id = area_row['researcharea_id']
                if old_area_id in area_mapping:
                    researcher.research_areas.add(area_mapping[old_area_id])

            researchers_created += 1

            if researchers_created % 50 == 0:
                self.stdout.write(f'  Imported {researchers_created} researchers...')

        conn.close()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'Import complete: {researchers_created} researchers imported, '
            f'{researchers_skipped} skipped'
        ))

        # Show summary
        if not dry_run:
            self.stdout.write('\n=== Summary ===')
            self.stdout.write(f'Total researchers: {Researcher.objects.count()}')
            self.stdout.write(f'Research areas: {ResearchArea.objects.count()}')

            # Country breakdown
            self.stdout.write('\nBy Country:')
            from django.db.models import Count
            countries = Researcher.objects.values('country').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
            for c in countries:
                self.stdout.write(f'  {c["country"]}: {c["count"]}')
