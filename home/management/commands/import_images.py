"""
Import images from WordPress URLs for ResearchItem records.

Usage:
    python manage.py import_images

Options:
    --dry-run       Show what would be imported without downloading
    --skip-authors  Only import main images, skip author photos
    --limit N       Only process first N items
"""
import csv
import os
import requests
from io import BytesIO
from urllib.parse import urlparse

from django.core.files.images import ImageFile
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from wagtail.images.models import Image

from home.models import ResearchItem


class Command(BaseCommand):
    help = 'Import images from WordPress URLs for research items'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without downloading',
        )
        parser.add_argument(
            '--skip-authors',
            action='store_true',
            help='Only import main images, skip author photos',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Only process first N items (0 = all)',
        )
        parser.add_argument(
            '--csv-file',
            type=str,
            default='1-setup files/research_items_definition/APS-Research-Export-2025-December-13-1610.csv',
            help='Path to CSV file',
        )

    def download_image(self, url, title_hint):
        """Download image from URL and return ImageFile."""
        if not url or not url.startswith('http'):
            return None

        try:
            self.stdout.write(f"    Downloading: {url[:60]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Get filename from URL
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = f"{slugify(title_hint)}.jpg"

            # Create ImageFile
            image_file = ImageFile(
                BytesIO(response.content),
                name=filename
            )
            return image_file

        except requests.RequestException as e:
            self.stdout.write(self.style.WARNING(f"    Failed to download: {e}"))
            return None

    def create_wagtail_image(self, image_file, title):
        """Create Wagtail Image from downloaded file."""
        if not image_file:
            return None

        try:
            image = Image(
                title=title[:255],
                file=image_file,
            )
            image.save()
            return image
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"    Failed to create image: {e}"))
            return None

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        skip_authors = options['skip_authors']
        limit = options['limit']
        csv_file = options['csv_file']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No images will be downloaded'))

        # Build lookup from CSV: slug -> image URLs
        image_data = {}
        with open(csv_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                slug = row.get('Slug', '').strip()
                if slug:
                    image_data[slug] = {
                        'main_image': row.get('wpcf-news-item-image', '').strip(),
                        'author_1_image': row.get('wpcf-author-image', '').strip(),
                        'author_2_image': row.get('wpcf-author-image-two', '').strip(),
                        'author_3_image': row.get('wpcf-author-image-three', '').strip(),
                    }

        # Process ResearchItems
        items = ResearchItem.objects.all().order_by('-publish_date')
        if limit:
            items = items[:limit]

        stats = {'main': 0, 'author1': 0, 'author2': 0, 'author3': 0, 'skipped': 0, 'errors': 0}

        for item in items:
            self.stdout.write(f"\n{item.short_title}")

            urls = image_data.get(item.slug, {})
            if not urls:
                self.stdout.write(self.style.WARNING("  No image data found in CSV"))
                stats['skipped'] += 1
                continue

            # Main image
            if not item.main_image and urls.get('main_image'):
                if dry_run:
                    self.stdout.write(f"  Would download main image: {urls['main_image'][:50]}...")
                else:
                    image_file = self.download_image(urls['main_image'], item.short_title)
                    if image_file:
                        wagtail_image = self.create_wagtail_image(
                            image_file,
                            f"{item.short_title} - Main Figure"
                        )
                        if wagtail_image:
                            item.main_image = wagtail_image
                            item.save()
                            self.stdout.write(self.style.SUCCESS("    Main image imported"))
                            stats['main'] += 1
                        else:
                            stats['errors'] += 1
                    else:
                        stats['errors'] += 1
            elif item.main_image:
                self.stdout.write("  Main image already exists, skipping")

            # Author images
            if not skip_authors:
                # Author 1
                if not item.author_1_image and urls.get('author_1_image'):
                    if dry_run:
                        self.stdout.write(f"  Would download author 1 image")
                    else:
                        image_file = self.download_image(urls['author_1_image'], f"{item.short_title}-author1")
                        if image_file:
                            wagtail_image = self.create_wagtail_image(
                                image_file,
                                f"{item.short_title} - Author 1"
                            )
                            if wagtail_image:
                                item.author_1_image = wagtail_image
                                item.save()
                                self.stdout.write(self.style.SUCCESS("    Author 1 image imported"))
                                stats['author1'] += 1

                # Author 2
                if not item.author_2_image and urls.get('author_2_image'):
                    if dry_run:
                        self.stdout.write(f"  Would download author 2 image")
                    else:
                        image_file = self.download_image(urls['author_2_image'], f"{item.short_title}-author2")
                        if image_file:
                            wagtail_image = self.create_wagtail_image(
                                image_file,
                                f"{item.short_title} - Author 2"
                            )
                            if wagtail_image:
                                item.author_2_image = wagtail_image
                                item.save()
                                self.stdout.write(self.style.SUCCESS("    Author 2 image imported"))
                                stats['author2'] += 1

                # Author 3
                if not item.author_3_image and urls.get('author_3_image'):
                    if dry_run:
                        self.stdout.write(f"  Would download author 3 image")
                    else:
                        image_file = self.download_image(urls['author_3_image'], f"{item.short_title}-author3")
                        if image_file:
                            wagtail_image = self.create_wagtail_image(
                                image_file,
                                f"{item.short_title} - Author 3"
                            )
                            if wagtail_image:
                                item.author_3_image = wagtail_image
                                item.save()
                                self.stdout.write(self.style.SUCCESS("    Author 3 image imported"))
                                stats['author3'] += 1

        # Summary
        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(self.style.SUCCESS(f"Main images imported: {stats['main']}"))
        self.stdout.write(f"Author 1 images: {stats['author1']}")
        self.stdout.write(f"Author 2 images: {stats['author2']}")
        self.stdout.write(f"Author 3 images: {stats['author3']}")
        self.stdout.write(f"Skipped (no data): {stats['skipped']}")
        self.stdout.write(self.style.WARNING(f"Errors: {stats['errors']}"))
