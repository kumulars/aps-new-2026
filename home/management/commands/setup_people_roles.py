"""
Management command to set up initial APS roles.
Run with: python manage.py setup_people_roles
"""
from django.core.management.base import BaseCommand
from home.models import APSRole, APSCommittee


class Command(BaseCommand):
    help = 'Set up initial APS roles and committees'

    def handle(self, *args, **options):
        # Define roles with their categories and display order
        roles_data = [
            # Officers (displayed in this order)
            ('President', 'officer', 1),
            ('President Elect', 'officer', 2),
            ('Immediate Past President', 'officer', 3),
            ('Secretary', 'officer', 4),
            ('Treasurer', 'officer', 5),

            # Councilors
            ('Councilor', 'councilor', 10),

            # Staff
            ('Society Manager', 'staff', 20),
            ('Web Developer', 'staff', 21),

            # Past Presidents
            ('Past President', 'past_president', 30),
        ]

        # Create or update roles
        created_count = 0
        updated_count = 0
        for name, category, display_order in roles_data:
            role, created = APSRole.objects.update_or_create(
                name=name,
                defaults={
                    'category': category,
                    'display_order': display_order,
                }
            )
            if created:
                created_count += 1
                self.stdout.write(f'  Created role: {name}')
            else:
                updated_count += 1
                self.stdout.write(f'  Updated role: {name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nRoles: {created_count} created, {updated_count} updated'
        ))

        # Define committees
        committees_data = [
            ('Awards Committee', 1),
            ('Symposium Site Selection Committee', 2),
            ('Membership Committee', 3),
            ('Student Activities Committee', 4),
            ('Communications Committee', 5),
            ('Young Investigators Committee', 6),
            ('Education Committee', 7),
            ('Diversity, Equity & Inclusion Committee', 8),
        ]

        # Create committees
        committee_created = 0
        committee_updated = 0
        for name, display_order in committees_data:
            committee, created = APSCommittee.objects.update_or_create(
                name=name,
                defaults={
                    'display_order': display_order,
                }
            )
            if created:
                committee_created += 1
                self.stdout.write(f'  Created committee: {name}')
            else:
                committee_updated += 1
                self.stdout.write(f'  Updated committee: {name}')

        self.stdout.write(self.style.SUCCESS(
            f'\nCommittees: {committee_created} created, {committee_updated} updated'
        ))

        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Go to Wagtail Admin > Snippets > APS People')
        self.stdout.write('2. Add people and assign roles/committees')
        self.stdout.write('3. Create a PeopleIndexPage under your site root')
