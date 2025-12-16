"""
Import images from WordPress into Wagtail for Global Peptide Groups.

Scans all GlobalPeptideGroupPage tab content for WordPress image URLs,
downloads them, uploads to Wagtail's image library, and updates the HTML.

Usage:
    python manage.py import_gpg_images
    python manage.py import_gpg_images --dry-run
"""

import os
import re
import requests
import tempfile
from urllib.parse import urlparse, unquote
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from wagtail.images.models import Image

from home.models import GlobalPeptideGroupPage


class Command(BaseCommand):
    help = 'Import WordPress images into Wagtail for Global Peptide Groups'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually downloading',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Pattern to find WordPress image URLs
        wp_image_pattern = re.compile(
            r'https://americanpeptidesociety\.org/wp-content/uploads/[^"\'>\s]+'
        )

        # Track all unique image URLs and their replacements
        url_mapping = {}

        # First pass: collect all unique image URLs
        self.stdout.write("Scanning for WordPress image URLs...")

        pages = GlobalPeptideGroupPage.objects.all()
        for page in pages:
            if not page.tabs:
                continue

            for tab in page.tabs.raw_data:
                content = tab['value']['content']
                urls = wp_image_pattern.findall(content)
                for url in urls:
                    if url not in url_mapping:
                        url_mapping[url] = None

        self.stdout.write(f"Found {len(url_mapping)} unique images to import")

        if dry_run:
            self.stdout.write("\nDry run - images that would be imported:")
            for url in sorted(url_mapping.keys()):
                filename = self.get_filename_from_url(url)
                self.stdout.write(f"  - {filename}")
            return

        # Second pass: download and upload images
        self.stdout.write("\nDownloading and uploading images...")

        success_count = 0
        error_count = 0

        for url in url_mapping.keys():
            filename = self.get_filename_from_url(url)
            self.stdout.write(f"  Processing: {filename}")

            try:
                # Check if image already exists in Wagtail
                existing = Image.objects.filter(title=filename).first()
                if existing:
                    self.stdout.write(f"    Already exists (ID: {existing.id})")
                    url_mapping[url] = existing
                    success_count += 1
                    continue

                # Download the image
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Save to temp file
                with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(filename)[1]) as tmp:
                    tmp.write(response.content)
                    tmp_path = tmp.name

                # Upload to Wagtail
                with open(tmp_path, 'rb') as f:
                    image = Image(title=filename)
                    image.file.save(filename, ImageFile(f))
                    image.save()

                # Clean up temp file
                os.unlink(tmp_path)

                url_mapping[url] = image
                self.stdout.write(self.style.SUCCESS(f"    Uploaded (ID: {image.id})"))
                success_count += 1

            except Exception as e:
                self.stdout.write(self.style.ERROR(f"    Error: {e}"))
                error_count += 1

        self.stdout.write(f"\nUploaded {success_count} images, {error_count} errors")

        # Third pass: update HTML in all pages
        self.stdout.write("\nUpdating page content with new image URLs...")

        pages_updated = 0
        for page in pages:
            if not page.tabs:
                continue

            tabs_data = page.tabs.raw_data
            page_modified = False

            for tab in tabs_data:
                content = tab['value']['content']
                original_content = content

                for old_url, image in url_mapping.items():
                    if image and old_url in content:
                        # Generate Wagtail image URL
                        new_url = image.file.url
                        content = content.replace(old_url, new_url)

                if content != original_content:
                    tab['value']['content'] = content
                    page_modified = True

            if page_modified:
                page.tabs = tabs_data
                page.save_revision().publish()
                self.stdout.write(f"  Updated: {page.title}")
                pages_updated += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nComplete! Updated {pages_updated} pages with local image URLs."
        ))

    def get_filename_from_url(self, url):
        """Extract filename from URL."""
        parsed = urlparse(url)
        path = unquote(parsed.path)
        return os.path.basename(path)
