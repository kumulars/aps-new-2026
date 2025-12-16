"""
Import people images from old project.
Run with: python manage.py import_people_images
"""
import os
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from home.models import APSPerson


class Command(BaseCommand):
    help = 'Import people images from old project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='/Users/larssahl/documents/wagtail/aps2026/media/people/',
            help='Source directory for images'
        )

    def handle(self, *args, **options):
        source_dir = options['source']

        if not os.path.exists(source_dir):
            self.stdout.write(self.style.ERROR(f'Source directory not found: {source_dir}'))
            return

        # Build a mapping of image files
        image_files = {}
        for filename in os.listdir(source_dir):
            if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                # Parse filename: lastname_firstname.jpg
                name_part = os.path.splitext(filename)[0].lower()
                parts = name_part.split('_')
                if len(parts) >= 2:
                    last_name = parts[0]
                    first_name = parts[1]
                    image_files[(last_name, first_name)] = os.path.join(source_dir, filename)

        self.stdout.write(f'Found {len(image_files)} image files')

        # Match to people
        matched = 0
        not_matched = 0

        for person in APSPerson.objects.filter(photo__isnull=True):
            # Try to find matching image
            last_lower = person.last_name.lower().replace(' ', '_').replace('.', '')
            first_lower = person.first_name.lower().replace(' ', '_').replace('.', '')

            # Handle names like "W. Seth" -> "seth"
            if first_lower.startswith('w._'):
                first_lower = first_lower.replace('w._', '')

            # Handle "James S." -> "james"
            first_lower = first_lower.split('_')[0] if '_' in first_lower else first_lower

            # Try exact match first
            image_path = image_files.get((last_lower, first_lower))

            # Try variations
            if not image_path:
                # Try just first part of first name
                for (last, first), path in image_files.items():
                    if last == last_lower and first.startswith(first_lower[:4]):
                        image_path = path
                        break

            if image_path:
                try:
                    with open(image_path, 'rb') as f:
                        image_file = ImageFile(f, name=os.path.basename(image_path))
                        wagtail_image = Image(
                            title=f'{person.first_name} {person.last_name}',
                            file=image_file
                        )
                        wagtail_image.save()

                        person.photo = wagtail_image
                        person.save()

                        matched += 1
                        self.stdout.write(f'  Matched: {person.full_name} <- {os.path.basename(image_path)}')
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f'  Error importing {image_path}: {e}'))
            else:
                not_matched += 1
                self.stdout.write(self.style.WARNING(f'  No image found for: {person.full_name}'))

        self.stdout.write(self.style.SUCCESS(f'\nImport complete: {matched} matched, {not_matched} not found'))
