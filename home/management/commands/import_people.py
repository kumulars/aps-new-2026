"""
Management command to import APS people from old project CSV.
Run with: python manage.py import_people
"""
import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from home.models import APSPerson, APSRole, PersonRoleAssignment


class Command(BaseCommand):
    help = 'Import APS people from CSV file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--csv',
            type=str,
            default='/Users/larssahl/documents/wagtail/aps2026/import_files/archive/clean_people_import.csv',
            help='Path to the CSV file'
        )

    def handle(self, *args, **options):
        csv_path = options['csv']

        # Map old category names to new role names
        role_mapping = {
            'President': 'President',
            'President Elect': 'President Elect',
            'Immediate Past President': 'Immediate Past President',
            'Past President': 'Past President',
            'Secretary': 'Secretary',
            'Treasurer': 'Treasurer',
            'Councilor': 'Councilor',
            'Cou': 'Councilor',  # Short form in some records
            'Association Manager': 'Society Manager',
            'Society Manager': 'Society Manager',
            'Web Developer': 'Web Developer',
        }

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                created_count = 0
                updated_count = 0
                skipped_count = 0

                for row in reader:
                    category = row.get('category', '').strip()
                    first_name = row.get('first_name', '').strip()
                    last_name = row.get('last_name', '').strip()
                    professional_title = row.get('professional_title', '').strip()
                    institution = row.get('institution', '').strip()
                    service_start = row.get('service_start_date', '').strip()
                    service_end = row.get('service_end_date', '').strip()

                    if not first_name or not last_name:
                        self.stdout.write(f'  Skipping row with missing name')
                        skipped_count += 1
                        continue

                    # Get or map the role
                    role_name = role_mapping.get(category)
                    if not role_name:
                        self.stdout.write(
                            self.style.WARNING(f'  Unknown category "{category}" for {first_name} {last_name}')
                        )
                        skipped_count += 1
                        continue

                    # Get the role object
                    try:
                        role = APSRole.objects.get(name=role_name)
                    except APSRole.DoesNotExist:
                        self.stdout.write(
                            self.style.WARNING(f'  Role "{role_name}" not found')
                        )
                        skipped_count += 1
                        continue

                    # Create or get the person
                    person, created = APSPerson.objects.get_or_create(
                        first_name=first_name,
                        last_name=last_name,
                        defaults={
                            'professional_title': professional_title,
                            'institution': institution,
                        }
                    )

                    if created:
                        created_count += 1
                        self.stdout.write(f'  Created: {first_name} {last_name}')
                    else:
                        # Update existing person info if needed
                        if not person.professional_title and professional_title:
                            person.professional_title = professional_title
                        if not person.institution and institution:
                            person.institution = institution
                        person.save()
                        updated_count += 1
                        self.stdout.write(f'  Updated: {first_name} {last_name}')

                    # Parse dates
                    start_date = None
                    end_date = None
                    if service_start:
                        try:
                            start_date = datetime.strptime(service_start, '%Y-%m-%d').date()
                        except ValueError:
                            pass
                    if service_end:
                        try:
                            end_date = datetime.strptime(service_end, '%Y-%m-%d').date()
                        except ValueError:
                            pass

                    # Determine if role is current (no end date or end date in future)
                    is_current = end_date is None or end_date > datetime.now().date()

                    # Create role assignment if it doesn't exist
                    assignment, ass_created = PersonRoleAssignment.objects.get_or_create(
                        person=person,
                        role=role,
                        defaults={
                            'service_start': start_date,
                            'service_end': end_date,
                            'is_current': is_current,
                        }
                    )

                    if not ass_created:
                        # Update existing assignment
                        assignment.service_start = start_date
                        assignment.service_end = end_date
                        assignment.is_current = is_current
                        assignment.save()

                self.stdout.write(self.style.SUCCESS(
                    f'\nImport complete: {created_count} created, {updated_count} updated, {skipped_count} skipped'
                ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {csv_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
