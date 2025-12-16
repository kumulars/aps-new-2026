"""
Import ResearchItem records from WordPress CSV export.

Usage:
    python manage.py import_research_items

Options:
    --dry-run    Show what would be imported without saving
    --year YYYY  Only import items from specified year (default: 2025)
"""
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from home.models import ResearchItem, ResearchItemCategory


class Command(BaseCommand):
    help = 'Import research items from WordPress CSV export'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without saving',
        )
        parser.add_argument(
            '--year',
            type=int,
            default=2025,
            help='Only import items from this year (default: 2025)',
        )
        parser.add_argument(
            '--csv-file',
            type=str,
            default='1-setup files/research_items_definition/APS-Research-Export-2025-December-13-1610.csv',
            help='Path to CSV file',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_year = options['year']
        csv_file = options['csv_file']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No data will be saved'))

        # Field mapping: CSV column -> model field
        field_map = {
            'wpcf-news-item-title': 'short_title',
            'wpcf-news-item-blurb': 'blurb',
            'wpcf-news-item-full-text': 'body',
            'wpcf-news-item-image-caption': 'main_image_caption',
            'wpcf-news-publication-full-title': 'publication_title',
            'wpcf-news-publication-authors': 'publication_authors',
            'wpcf-news-publication-citation': 'publication_citation',
            'wpcf-news-publication-url': 'publication_url',
            'wpcf-news-pi-first-name': 'pi_first_name',
            'wpcf-news-pi-last-name': 'pi_last_name',
            'wpcf-news-pi-title': 'pi_title',
            'wpcf-news-pi-institution-or-business': 'pi_institution',
            'wpcf-website-pi-url': 'pi_url',
            'wpcf-author-information': 'author_1_info',
            'wpcf-author-information-two': 'author_2_info',
            'wpcf-author-information-three': 'author_3_info',
            'Slug': 'slug',
        }

        imported = 0
        skipped = 0
        errors = []

        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Parse date - format is "12/13/25 14:09"
                date_str = row.get('Date', '').strip()
                if not date_str:
                    skipped += 1
                    continue

                try:
                    # Parse the date
                    parsed_date = datetime.strptime(date_str.split()[0], '%m/%d/%y')

                    # Filter by year
                    if parsed_date.year != target_year:
                        skipped += 1
                        continue
                except ValueError as e:
                    errors.append(f"Date parse error for '{date_str}': {e}")
                    skipped += 1
                    continue

                # Get short_title for display
                short_title = row.get('wpcf-news-item-title', '').strip()
                if not short_title:
                    short_title = row.get('Title', 'Untitled').strip()

                if not short_title:
                    skipped += 1
                    continue

                # Check if already exists
                slug = row.get('Slug', '').strip()
                if slug and ResearchItem.objects.filter(slug=slug).exists():
                    self.stdout.write(f"  Skipping (exists): {short_title}")
                    skipped += 1
                    continue

                # Build the model data
                item_data = {
                    'publish_date': parsed_date.date(),
                }

                # Map fields from CSV
                for csv_field, model_field in field_map.items():
                    value = row.get(csv_field, '').strip()
                    if value:
                        item_data[model_field] = value

                # Derive lab_name from PI last name if not empty
                pi_last = row.get('wpcf-news-pi-last-name', '').strip()
                if pi_last:
                    item_data['lab_name'] = f"{pi_last} Lab"
                else:
                    item_data['lab_name'] = "Research Lab"

                # Ensure required fields have defaults
                if 'body' not in item_data or not item_data['body']:
                    item_data['body'] = row.get('wpcf-news-item-blurb', '') or 'Content pending.'

                if 'publication_title' not in item_data:
                    item_data['publication_title'] = short_title

                if 'publication_authors' not in item_data:
                    item_data['publication_authors'] = ''

                if 'publication_citation' not in item_data:
                    item_data['publication_citation'] = ''

                if 'publication_url' not in item_data:
                    item_data['publication_url'] = ''

                if 'pi_first_name' not in item_data:
                    item_data['pi_first_name'] = ''

                if 'pi_last_name' not in item_data:
                    item_data['pi_last_name'] = ''

                if 'pi_institution' not in item_data:
                    item_data['pi_institution'] = ''

                if dry_run:
                    self.stdout.write(f"  Would import: {short_title} ({parsed_date.date()})")
                else:
                    try:
                        item = ResearchItem(**item_data)
                        item.save()
                        self.stdout.write(self.style.SUCCESS(f"  Imported: {short_title}"))
                    except Exception as e:
                        errors.append(f"Error saving '{short_title}': {e}")
                        continue

                imported += 1

        # Summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f"Imported: {imported}"))
        self.stdout.write(f"Skipped: {skipped}")

        if errors:
            self.stdout.write(self.style.ERROR(f"Errors: {len(errors)}"))
            for err in errors[:10]:  # Show first 10 errors
                self.stdout.write(self.style.ERROR(f"  {err}"))
