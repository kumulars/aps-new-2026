"""
Import symposium images from old aps2026 project.

Reads images from /Users/larssahl/documents/wagtail/aps2026/media/symposia-images/
and imports them into the new site's Wagtail image system.
"""

import os
from pathlib import Path

from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from wagtail.images.models import Image

from home.models import SymposiumImage


class Command(BaseCommand):
    help = 'Import symposium images from old aps2026 project'

    SOURCE_BASE = Path('/Users/larssahl/documents/wagtail/aps2026/media/symposia-images')

    YEARS = [2015, 2017, 2019, 2022, 2023, 2025]

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Only import a specific year',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of images per year (for testing)',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        target_year = options.get('year')
        limit = options.get('limit')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - no changes will be made'))

        years_to_process = [target_year] if target_year else self.YEARS

        total_imported = 0
        total_skipped = 0

        for year in years_to_process:
            source_dir = self.SOURCE_BASE / str(year) / 'full'

            if not source_dir.exists():
                self.stdout.write(self.style.WARNING(f'Source directory not found: {source_dir}'))
                continue

            self.stdout.write(f'\n=== Processing {year} ===')

            # Get list of images
            image_files = sorted([
                f for f in source_dir.iterdir()
                if f.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif']
            ])

            if limit:
                image_files = image_files[:limit]

            self.stdout.write(f'Found {len(image_files)} images')

            for idx, image_path in enumerate(image_files):
                # Generate a caption from filename (clean up underscores, numbers)
                caption = self._generate_caption(image_path.stem)

                if dry_run:
                    self.stdout.write(f'  Would import: {image_path.name} -> "{caption}"')
                    total_imported += 1
                    continue

                # Check if image already exists by title
                wagtail_title = f"Symposium {year} - {image_path.stem}"

                existing = Image.objects.filter(title=wagtail_title).first()
                if existing:
                    # Check if SymposiumImage record exists
                    if SymposiumImage.objects.filter(image=existing, year=year).exists():
                        self.stdout.write(f'  Skipping (exists): {image_path.name}')
                        total_skipped += 1
                        continue

                try:
                    # Import into Wagtail
                    with open(image_path, 'rb') as f:
                        wagtail_image = Image(title=wagtail_title)
                        wagtail_image.file.save(image_path.name, ImageFile(f), save=True)

                    # Create SymposiumImage record
                    SymposiumImage.objects.create(
                        year=year,
                        image=wagtail_image,
                        caption=caption,
                        sort_order=idx
                    )

                    self.stdout.write(self.style.SUCCESS(f'  Imported: {image_path.name}'))
                    total_imported += 1

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'  Error importing {image_path.name}: {e}'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Import complete: {total_imported} imported, {total_skipped} skipped'))

    def _generate_caption(self, filename):
        """
        Generate a readable caption from filename.
        e.g., 'finan_brian_2' -> 'Finan Brian'
        """
        # Remove trailing numbers
        parts = filename.split('_')
        # Filter out pure numbers
        words = [p for p in parts if not p.isdigit()]
        # Capitalize each word
        caption = ' '.join(w.capitalize() for w in words)
        return caption
