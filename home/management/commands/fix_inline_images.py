"""
Fix inline images in ResearchItem body content.

This command:
1. Downloads images from WordPress URLs to local storage
2. Updates src attributes to point to local files
3. Replaces 'img-responsive' class with 'img-fluid' (Bootstrap 3 → 5)

Usage:
    python manage.py fix_inline_images
    python manage.py fix_inline_images --dry-run
    python manage.py fix_inline_images --limit 5
"""
import os
import re
import requests
from urllib.parse import urlparse, urljoin
from io import BytesIO

from django.core.management.base import BaseCommand
from django.conf import settings

from home.models import ResearchItem


class Command(BaseCommand):
    help = 'Fix inline images in research item body content'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be changed without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=0,
            help='Only process first N items (0 = all)',
        )
        parser.add_argument(
            '--skip-download',
            action='store_true',
            help='Only fix CSS classes, skip image downloads',
        )

    def download_image(self, url, save_dir):
        """Download image from URL and save locally. Returns local path or None."""
        if not url or not url.startswith('http'):
            return None

        try:
            self.stdout.write(f"      Downloading: {url[:70]}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            # Get filename from URL
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                return None

            # Ensure save directory exists
            os.makedirs(save_dir, exist_ok=True)

            # Save file
            local_path = os.path.join(save_dir, filename)
            with open(local_path, 'wb') as f:
                f.write(response.content)

            # Return the URL path for use in HTML
            relative_path = os.path.relpath(local_path, settings.MEDIA_ROOT)
            return f"{settings.MEDIA_URL}{relative_path}"

        except requests.RequestException as e:
            self.stdout.write(self.style.WARNING(f"      Failed to download: {e}"))
            return None
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"      Error saving: {e}"))
            return None

    def process_body(self, body, save_dir, dry_run=False, skip_download=False):
        """Process body HTML, download images and fix classes."""
        if not body:
            return body, {'images_found': 0, 'images_downloaded': 0, 'classes_fixed': 0}

        stats = {'images_found': 0, 'images_downloaded': 0, 'classes_fixed': 0}
        new_body = body

        # Find all img tags with WordPress URLs
        # Match various WordPress URL patterns
        wp_domains = [
            'americanpeptidesociety.org',
            'www.americanpeptidesociety.org',
        ]

        # Regex to find img tags with src attribute
        img_pattern = re.compile(
            r'<img\s+([^>]*?)src=["\']([^"\']+)["\']([^>]*?)>',
            re.IGNORECASE | re.DOTALL
        )

        def replace_img(match):
            nonlocal stats
            prefix = match.group(1)
            src = match.group(2)
            suffix = match.group(3)

            # Check if this is a WordPress URL
            parsed = urlparse(src)
            is_wp_url = any(domain in parsed.netloc for domain in wp_domains)

            new_src = src
            if is_wp_url:
                stats['images_found'] += 1
                if not skip_download and not dry_run:
                    local_path = self.download_image(src, save_dir)
                    if local_path:
                        new_src = local_path
                        stats['images_downloaded'] += 1
                elif dry_run:
                    self.stdout.write(f"      Would download: {src[:60]}...")

            # Reconstruct the img tag
            full_tag = f'<img {prefix}src="{new_src}"{suffix}>'
            return full_tag

        new_body = img_pattern.sub(replace_img, new_body)

        # Replace img-responsive with img-fluid
        responsive_count = new_body.count('img-responsive')
        if responsive_count > 0:
            stats['classes_fixed'] = responsive_count
            if not dry_run:
                new_body = new_body.replace('img-responsive', 'img-fluid')
            else:
                self.stdout.write(f"      Would replace {responsive_count} 'img-responsive' → 'img-fluid'")

        return new_body, stats

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        skip_download = options['skip_download']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - No changes will be made'))

        # Directory to save inline images
        save_dir = os.path.join(settings.MEDIA_ROOT, 'inline_images')

        # Get items to process
        items = ResearchItem.objects.all().order_by('-publish_date')
        if limit:
            items = items[:limit]

        total_stats = {
            'items_processed': 0,
            'items_modified': 0,
            'images_found': 0,
            'images_downloaded': 0,
            'classes_fixed': 0,
        }

        for item in items:
            self.stdout.write(f"\n  {item.short_title}")
            total_stats['items_processed'] += 1

            if not item.body:
                self.stdout.write("    No body content, skipping")
                continue

            new_body, stats = self.process_body(
                item.body,
                save_dir,
                dry_run=dry_run,
                skip_download=skip_download
            )

            total_stats['images_found'] += stats['images_found']
            total_stats['images_downloaded'] += stats['images_downloaded']
            total_stats['classes_fixed'] += stats['classes_fixed']

            # Check if anything changed
            if new_body != item.body:
                total_stats['items_modified'] += 1
                if not dry_run:
                    item.body = new_body
                    item.save()
                    self.stdout.write(self.style.SUCCESS("    Updated"))
                else:
                    self.stdout.write("    Would update")
            else:
                if stats['images_found'] == 0 and stats['classes_fixed'] == 0:
                    self.stdout.write("    No WordPress images or img-responsive classes found")

        # Summary
        self.stdout.write("\n" + "=" * 60)
        self.stdout.write(self.style.SUCCESS(f"Items processed: {total_stats['items_processed']}"))
        self.stdout.write(f"Items modified: {total_stats['items_modified']}")
        self.stdout.write(f"WordPress images found: {total_stats['images_found']}")
        self.stdout.write(f"Images downloaded: {total_stats['images_downloaded']}")
        self.stdout.write(f"'img-responsive' classes fixed: {total_stats['classes_fixed']}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\nThis was a dry run. Run without --dry-run to apply changes."))
