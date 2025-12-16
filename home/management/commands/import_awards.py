"""
Import awards from old project CSV.
Run with: python manage.py import_awards
"""
import csv
import re
from django.core.management.base import BaseCommand
from home.models import AwardType, AwardRecipient


class Command(BaseCommand):
    help = 'Import awards from CSV and set up award types'

    def handle(self, *args, **options):
        # First, create the award types
        self.create_award_types()

        # Then import recipients
        self.import_recipients()

    def create_award_types(self):
        """Create the 6 award types with descriptions."""

        award_types_data = [
            {
                'slug': 'merrifield',
                'name': 'R. Bruce Merrifield Award',
                'short_name': 'Merrifield',
                'display_order': 1,
                'description': '''The R. Bruce Merrifield Award is the most prestigious honor bestowed by the American Peptide Society, recognizing outstanding career achievements in peptide science. The award is named in honor of R. Bruce Merrifield, who revolutionized peptide synthesis with his invention of solid-phase peptide synthesis, for which he received the Nobel Prize in Chemistry in 1984.

The award recognizes scientists who have made exceptional contributions to the field of peptide research throughout their careers, demonstrating sustained excellence in innovation, discovery, and advancement of peptide science.''',
                'additional_content': '<p><strong>Learn more:</strong> <a href="https://americanpeptidesociety.org/merrifield-essay/">Read about Bruce Merrifield and the history of this award</a></p>',
            },
            {
                'slug': 'duvigneaud',
                'name': 'Vincent du Vigneaud Award',
                'short_name': 'du Vigneaud',
                'display_order': 2,
                'description': '''The Vincent du Vigneaud Award recognizes outstanding achievements in peptide research by scientists who have demonstrated exceptional creativity and productivity in the field. Named after Vincent du Vigneaud, who received the Nobel Prize in Chemistry in 1955 for his work on biochemically important sulfur compounds and the first synthesis of a polypeptide hormone (oxytocin).

This award honors researchers who have made significant contributions to our understanding of peptide chemistry, biology, and their applications.''',
            },
            {
                'slug': 'goodman',
                'name': 'Murray Goodman Scientific Excellence & Mentorship Award',
                'short_name': 'Goodman',
                'display_order': 3,
                'description': '''The Murray Goodman Scientific Excellence and Mentorship Award recognizes career-long research excellence in peptide science combined with significant mentorship and training of students, postdoctoral fellows, and other co-workers. The award honors the legacy of Murray Goodman, a pioneering peptide chemist who was renowned both for his scientific contributions and his dedication to training the next generation of scientists.

This award celebrates researchers who exemplify the dual commitment to scientific excellence and mentorship that characterized Murray Goodman's distinguished career.''',
            },
            {
                'slug': 'makineni',
                'name': 'Rao Makineni Lectureship',
                'short_name': 'Makineni',
                'display_order': 4,
                'description': '''The Rao Makineni Lectureship honors scientists who have made significant contributions to peptide science in industry or academic-industry collaborations. The award recognizes the important role that industrial research plays in advancing peptide science and translating discoveries into practical applications.

Named in honor of Rao Makineni, this lectureship celebrates researchers who bridge the gap between fundamental research and real-world applications of peptide science.''',
            },
            {
                'slug': 'early-career',
                'name': 'APS Early Career Investigator Lectureship',
                'short_name': 'Early Career',
                'display_order': 5,
                'description': '''The APS Early Career Investigator Lectureship recognizes outstanding research achievements by scientists in the early stages of their independent careers. This award highlights promising young investigators who have already made significant contributions to peptide science and are poised to become future leaders in the field.

The award aims to support and encourage the next generation of peptide scientists by providing recognition and visibility for their innovative work.''',
            },
            {
                'slug': 'hirschmann',
                'name': 'Ralph F. Hirschmann Award',
                'short_name': 'Hirschmann',
                'display_order': 6,
                'description': '''The Ralph F. Hirschmann Award in Peptide Chemistry is presented by the American Chemical Society in recognition of outstanding contributions to peptide chemistry. While administered by the ACS, this prestigious award is closely associated with the American Peptide Society and the peptide research community.

Named after Ralph F. Hirschmann, a pioneering medicinal chemist who made fundamental contributions to peptide synthesis and drug discovery, this award honors researchers who have advanced the field of peptide chemistry through innovative research.''',
            },
        ]

        for data in award_types_data:
            award_type, created = AwardType.objects.update_or_create(
                slug=data['slug'],
                defaults={
                    'name': data['name'],
                    'short_name': data['short_name'],
                    'description': data['description'],
                    'additional_content': data.get('additional_content', ''),
                    'display_order': data['display_order'],
                    'is_active': True,
                }
            )
            status = 'Created' if created else 'Updated'
            self.stdout.write(f'{status}: {data["name"]}')

        self.stdout.write(self.style.SUCCESS(f'\nAward types set up successfully'))

    def import_recipients(self):
        """Import recipients from CSV."""
        csv_path = '/Users/larssahl/documents/wagtail/aps2026/import_files/awards_cleaned.csv'

        # Map CSV award names to our slugs
        award_mapping = {
            'merrifield': 'merrifield',
            'merrifeild': 'merrifield',  # Handle typo in data
            'duvigneaud': 'duvigneaud',
            'goodman': 'goodman',
            'makineni': 'makineni',
            'early-career': 'early-career',
            'hirschmann': 'hirschmann',
        }

        created_count = 0
        updated_count = 0
        skipped_count = 0

        try:
            with open(csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)

                for row in reader:
                    award_name_raw = row.get('wpcf-award_name', '').strip().lower()
                    award_slug = award_mapping.get(award_name_raw)

                    if not award_slug:
                        skipped_count += 1
                        continue

                    try:
                        award_type = AwardType.objects.get(slug=award_slug)
                    except AwardType.DoesNotExist:
                        self.stdout.write(self.style.WARNING(f'Award type not found: {award_slug}'))
                        skipped_count += 1
                        continue

                    year_str = row.get('wpcf-award-year', '').strip()
                    if not year_str:
                        skipped_count += 1
                        continue

                    try:
                        year = int(year_str)
                    except ValueError:
                        skipped_count += 1
                        continue

                    first_name = row.get('wpcf-awardee_fname', '').strip()
                    last_name = row.get('wpcf-awardee_lname', '').strip()

                    if not first_name or not last_name:
                        skipped_count += 1
                        continue

                    institution = row.get('wpcf-awardee_institution', '').strip()
                    biography = row.get('wpcf-awardee_description', '').strip()

                    # Clean up biography (remove HTML tags for plain text storage)
                    if biography:
                        biography = re.sub(r'<[^>]+>', '', biography)
                        biography = biography.replace('&emdash;', '—')
                        biography = biography.replace('&nbsp;', ' ')
                        biography = ' '.join(biography.split())  # Normalize whitespace

                    recipient, created = AwardRecipient.objects.update_or_create(
                        award_type=award_type,
                        year=year,
                        last_name=last_name,
                        defaults={
                            'first_name': first_name,
                            'institution': institution,
                            'biography': biography,
                        }
                    )

                    if created:
                        created_count += 1
                    else:
                        updated_count += 1

            self.stdout.write(self.style.SUCCESS(
                f'\nRecipients: {created_count} created, {updated_count} updated, {skipped_count} skipped'
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'CSV file not found: {csv_path}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error: {e}'))
