"""
Management command to migrate local media files to DigitalOcean Spaces.

Usage:
    # Dry run (see what would be uploaded)
    python manage.py migrate_media_to_spaces --dry-run

    # Actually migrate files
    python manage.py migrate_media_to_spaces

    # Skip files that already exist in Spaces
    python manage.py migrate_media_to_spaces --skip-existing

    # Only migrate specific subdirectory
    python manage.py migrate_media_to_spaces --subdir=images
"""

import mimetypes
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

try:
    import boto3
    from botocore.exceptions import ClientError
except ImportError:
    boto3 = None


class Command(BaseCommand):
    help = 'Migrate local media files to DigitalOcean Spaces'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be uploaded without actually uploading',
        )
        parser.add_argument(
            '--skip-existing',
            action='store_true',
            help='Skip files that already exist in Spaces',
        )
        parser.add_argument(
            '--subdir',
            type=str,
            default='',
            help='Only migrate a specific subdirectory (e.g., "images" or "documents")',
        )
        parser.add_argument(
            '--media-root',
            type=str,
            default='',
            help='Override MEDIA_ROOT path (useful if running from different location)',
        )

    def handle(self, *args, **options):
        if boto3 is None:
            raise CommandError(
                'boto3 is not installed. Run: pip install boto3'
            )

        dry_run = options['dry_run']
        skip_existing = options['skip_existing']
        subdir = options['subdir']

        # Get media root
        media_root = options['media_root'] or getattr(settings, 'MEDIA_ROOT', None)
        if not media_root:
            raise CommandError('MEDIA_ROOT is not configured')

        media_root = Path(media_root)
        if subdir:
            media_root = media_root / subdir

        if not media_root.exists():
            raise CommandError(f'Media directory does not exist: {media_root}')

        # Get Spaces configuration
        access_key = os.environ.get('SPACES_ACCESS_KEY') or getattr(settings, 'AWS_ACCESS_KEY_ID', None)
        secret_key = os.environ.get('SPACES_SECRET_KEY') or getattr(settings, 'AWS_SECRET_ACCESS_KEY', None)
        bucket_name = os.environ.get('SPACES_BUCKET_NAME') or getattr(settings, 'AWS_STORAGE_BUCKET_NAME', None)
        region = os.environ.get('SPACES_REGION') or getattr(settings, 'AWS_S3_REGION_NAME', 'nyc3')
        endpoint_url = f'https://{region}.digitaloceanspaces.com'

        # The prefix in the bucket (e.g., 'media')
        bucket_prefix = getattr(settings, 'AWS_LOCATION', 'media')

        if not all([access_key, secret_key, bucket_name]):
            raise CommandError(
                'Spaces credentials not configured. Set SPACES_ACCESS_KEY, '
                'SPACES_SECRET_KEY, and SPACES_BUCKET_NAME environment variables '
                'or configure AWS_* settings.'
            )

        self.stdout.write(self.style.NOTICE(f'Configuration:'))
        self.stdout.write(f'  Media root: {media_root}')
        self.stdout.write(f'  Bucket: {bucket_name}')
        self.stdout.write(f'  Region: {region}')
        self.stdout.write(f'  Prefix: {bucket_prefix}/')
        self.stdout.write(f'  Dry run: {dry_run}')
        self.stdout.write(f'  Skip existing: {skip_existing}')
        self.stdout.write('')

        # Create S3 client
        s3_client = boto3.client(
            's3',
            region_name=region,
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
        )

        # Verify bucket access
        try:
            s3_client.head_bucket(Bucket=bucket_name)
            self.stdout.write(self.style.SUCCESS(f'Connected to bucket: {bucket_name}'))
        except ClientError as e:
            raise CommandError(f'Cannot access bucket {bucket_name}: {e}')

        # Get existing files in bucket (for skip-existing)
        existing_keys = set()
        if skip_existing:
            self.stdout.write('Fetching existing files in Spaces...')
            paginator = s3_client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=bucket_name, Prefix=f'{bucket_prefix}/'):
                for obj in page.get('Contents', []):
                    existing_keys.add(obj['Key'])
            self.stdout.write(f'Found {len(existing_keys)} existing files in Spaces')

        # Collect files to upload
        files_to_upload = []
        total_size = 0

        # Get the base media root for calculating relative paths
        base_media_root = Path(getattr(settings, 'MEDIA_ROOT', media_root))

        for file_path in media_root.rglob('*'):
            if file_path.is_file():
                # Calculate the key (path in bucket)
                try:
                    relative_path = file_path.relative_to(base_media_root)
                except ValueError:
                    relative_path = file_path.relative_to(media_root)

                key = f'{bucket_prefix}/{relative_path}'

                # Check if we should skip this file
                if skip_existing and key in existing_keys:
                    continue

                file_size = file_path.stat().st_size
                files_to_upload.append((file_path, key, file_size))
                total_size += file_size

        if not files_to_upload:
            self.stdout.write(self.style.SUCCESS('No files to upload!'))
            return

        # Show summary
        self.stdout.write('')
        self.stdout.write(f'Files to upload: {len(files_to_upload)}')
        self.stdout.write(f'Total size: {self._format_size(total_size)}')
        self.stdout.write('')

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN - Files that would be uploaded:'))
            for file_path, key, size in files_to_upload[:20]:
                self.stdout.write(f'  {key} ({self._format_size(size)})')
            if len(files_to_upload) > 20:
                self.stdout.write(f'  ... and {len(files_to_upload) - 20} more files')
            return

        # Upload files
        uploaded = 0
        failed = 0
        uploaded_size = 0

        for i, (file_path, key, size) in enumerate(files_to_upload, 1):
            try:
                # Guess content type
                content_type, _ = mimetypes.guess_type(str(file_path))
                if content_type is None:
                    content_type = 'application/octet-stream'

                # Upload with public-read ACL
                extra_args = {
                    'ACL': 'public-read',
                    'ContentType': content_type,
                    'CacheControl': 'max-age=86400',
                }

                s3_client.upload_file(
                    str(file_path),
                    bucket_name,
                    key,
                    ExtraArgs=extra_args,
                )

                uploaded += 1
                uploaded_size += size

                # Progress update every 10 files or on last file
                if i % 10 == 0 or i == len(files_to_upload):
                    progress = (i / len(files_to_upload)) * 100
                    self.stdout.write(
                        f'Progress: {i}/{len(files_to_upload)} ({progress:.1f}%) - '
                        f'{self._format_size(uploaded_size)} uploaded'
                    )

            except Exception as e:
                failed += 1
                self.stdout.write(
                    self.style.ERROR(f'Failed to upload {key}: {e}')
                )

        # Final summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(f'Migration complete!'))
        self.stdout.write(f'  Uploaded: {uploaded} files ({self._format_size(uploaded_size)})')
        if failed:
            self.stdout.write(self.style.ERROR(f'  Failed: {failed} files'))

        self.stdout.write('')
        self.stdout.write('Files are now available at:')
        self.stdout.write(f'  https://{bucket_name}.{region}.digitaloceanspaces.com/{bucket_prefix}/')

    def _format_size(self, size_bytes):
        """Format bytes as human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f'{size_bytes:.1f} {unit}'
            size_bytes /= 1024
        return f'{size_bytes:.1f} TB'
