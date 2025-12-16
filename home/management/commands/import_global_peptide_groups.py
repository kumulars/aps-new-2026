"""
Import Global Peptide Groups from Lab of the Month HTML files.

Parses WPBakery shortcodes to extract tabbed content and creates
GlobalPeptideGroupPage entries under the GlobalPeptideGroupIndexPage.

Usage:
    python manage.py import_global_peptide_groups
"""

import os
import re
from datetime import date
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from wagtail.models import Page

from home.models import GlobalPeptideGroupPage, GlobalPeptideGroupIndexPage


# Mapping of folder names to group data
# Format: (folder_name, lab_name, pi_name, institution, feature_date, old_url_slug)
LAB_DATA = [
    {
        'folder': '14 - Craik Lab',
        'file': 'craik_lab.html',
        'lab_name': 'The Craik Group',
        'pi_name': 'David J. Craik',
        'institution': 'Institute for Molecular Bioscience, University of Queensland',
        'feature_date': date(2025, 11, 1),  # November 2025
        'old_url_slug': 'craik-lab-november-2025',
        'is_current': True,
    },
    {
        'folder': '15 - DECEMBER - Sun Group',
        'file': 'hao_lab_full.html_lab.html',
        'lab_name': 'The Sun Group',
        'pi_name': 'Hao Sun',
        'institution': 'College of Sciences, Nanjing Agricultural University',
        'feature_date': date(2025, 12, 1),  # December 2025
        'old_url_slug': 'sun-group-december-2025',
        'is_current': False,
    },
    {
        'folder': '13 - Sep-Oct-2025-Del_Valle_Group',
        'file': 'del_valle_group.html',
        'lab_name': 'The Del Valle Group',
        'pi_name': 'Juan R. Del Valle',
        'institution': 'University of Notre Dame',
        'feature_date': date(2025, 9, 1),  # September 2025
        'old_url_slug': 'del-valle-group-september-2025',
        'is_current': False,
    },
    {
        'folder': '7 - MAY \'25 - Nicola D\'Amelio',
        'file': 'damelio_lab.html',
        'lab_name': 'The D\'Amelio Group',
        'pi_name': 'Nicola D\'Amelio',
        'institution': 'National Research Council of Italy',
        'feature_date': date(2025, 5, 1),  # May 2025
        'old_url_slug': 'damelio-lab-may-2025',
        'is_current': False,
    },
    {
        'folder': '7 - APRIL \'25 Liu Lab',
        'file': 'liu_lab.html',
        'lab_name': 'The Liu Lab',
        'pi_name': 'Rudi Fasan',
        'institution': 'University of Texas at Dallas',
        'feature_date': date(2025, 4, 1),  # April 2025
        'old_url_slug': 'liu-lab-april-2025',
        'is_current': False,
    },
    {
        'folder': '5 - JANUARY \'25',
        'file': None,  # Will search for main HTML file
        'lab_name': 'The Kay Group',
        'pi_name': '',
        'institution': '',
        'feature_date': date(2025, 1, 1),  # January 2025
        'old_url_slug': 'kay-group-january-2025',
        'is_current': False,
    },
    {
        'folder': '4 - DECEMBER_Schmeing Lab',
        'file': None,  # Will search for main HTML file
        'lab_name': 'The Schmeing Lab',
        'pi_name': 'T. Martin Schmeing',
        'institution': 'McGill University',
        'feature_date': date(2024, 12, 1),  # December 2024
        'old_url_slug': 'schmeing-lab-december-2024',
        'is_current': False,
    },
    {
        'folder': '3-NOVEMBER_David_lab',
        'file': None,  # Will search for main HTML file
        'lab_name': 'The David Lab',
        'pi_name': 'Yael David',
        'institution': 'Memorial Sloan Kettering Cancer Center',
        'feature_date': date(2024, 11, 1),  # November 2024
        'old_url_slug': 'david-lab-november-2024',
        'is_current': False,
    },
    {
        'folder': '2-OCTOBER_Kiessling_lab',
        'file': '2_kiessling_page.php',
        'lab_name': 'The Kiessling Lab',
        'pi_name': 'Laura L. Kiessling',
        'institution': 'MIT',
        'feature_date': date(2024, 10, 1),  # October 2024
        'old_url_slug': 'kiessling-lab-october-2024',
        'is_current': False,
    },
    {
        'folder': '1-SEPTEMBER_24_Nitsche_Lab',
        'file': None,  # Will search for main HTML file
        'lab_name': 'The Nitsche Lab',
        'pi_name': 'Christoph Nitsche',
        'institution': 'Australian National University',
        'feature_date': date(2024, 9, 1),  # September 2024
        'old_url_slug': 'nitsche-lab-september-2024',
        'is_current': False,
    },
]


class Command(BaseCommand):
    help = 'Import Global Peptide Groups from Lab of the Month HTML files'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without actually creating pages',
        )
        parser.add_argument(
            '--folder',
            type=str,
            help='Only import from a specific folder',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        specific_folder = options.get('folder')

        base_path = '/Users/larssahl/documents/wagtail/aps-new-2026/lab-of-the-month/1-contributions'

        # Get or create the index page
        try:
            index_page = GlobalPeptideGroupIndexPage.objects.get()
            self.stdout.write(f"Found existing index page: {index_page.title}")
        except GlobalPeptideGroupIndexPage.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                "GlobalPeptideGroupIndexPage not found. Please create one in the admin first."
            ))
            return
        except GlobalPeptideGroupIndexPage.MultipleObjectsReturned:
            index_page = GlobalPeptideGroupIndexPage.objects.first()
            self.stdout.write(f"Multiple index pages found, using: {index_page.title}")

        imported_count = 0
        skipped_count = 0

        for lab_data in LAB_DATA:
            folder_name = lab_data['folder']

            # Filter by specific folder if provided
            if specific_folder and specific_folder not in folder_name:
                continue

            folder_path = os.path.join(base_path, folder_name)

            if not os.path.exists(folder_path):
                self.stdout.write(self.style.WARNING(f"Folder not found: {folder_path}"))
                skipped_count += 1
                continue

            # Find the HTML file
            html_file = lab_data.get('file')
            if html_file:
                file_path = os.path.join(folder_path, html_file)
            else:
                # Search for the main HTML file
                file_path = self.find_main_html_file(folder_path)

            if not file_path or not os.path.exists(file_path):
                self.stdout.write(self.style.WARNING(
                    f"HTML file not found for {folder_name}"
                ))
                skipped_count += 1
                continue

            self.stdout.write(f"\nProcessing: {folder_name}")
            self.stdout.write(f"  File: {os.path.basename(file_path)}")

            # Parse the HTML file
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error reading file: {e}"))
                skipped_count += 1
                continue

            # Extract tabs from WPBakery shortcodes
            tabs = self.extract_tabs(html_content)

            if not tabs:
                self.stdout.write(self.style.WARNING(f"  No tabs found in {file_path}"))
                skipped_count += 1
                continue

            self.stdout.write(f"  Found {len(tabs)} tabs: {[t['title'] for t in tabs]}")

            # Create the page title
            page_title = f"Global Peptide Groups - {lab_data['lab_name']}"
            slug = slugify(lab_data['lab_name'])

            # Check if page already exists
            existing = GlobalPeptideGroupPage.objects.filter(slug=slug).first()
            if existing:
                self.stdout.write(self.style.WARNING(f"  Page already exists: {existing.title}"))
                skipped_count += 1
                continue

            if dry_run:
                self.stdout.write(self.style.SUCCESS(f"  Would create: {page_title}"))
                imported_count += 1
                continue

            # Build tabs StreamField data
            tabs_data = []
            for tab in tabs:
                tabs_data.append({
                    'type': 'tab',
                    'value': {
                        'title': tab['title'],
                        'content': tab['content'],
                    }
                })

            # Create the page
            page = GlobalPeptideGroupPage(
                title=page_title,
                slug=slug,
                lab_name=lab_data['lab_name'],
                pi_name=lab_data.get('pi_name', ''),
                institution=lab_data.get('institution', ''),
                feature_date=lab_data.get('feature_date'),
                is_current=lab_data.get('is_current', False),
                old_url_slug=lab_data.get('old_url_slug', ''),
                tabs=tabs_data,
            )

            try:
                index_page.add_child(instance=page)
                page.save_revision().publish()
                self.stdout.write(self.style.SUCCESS(f"  Created: {page_title}"))
                imported_count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"  Error creating page: {e}"))
                skipped_count += 1

        self.stdout.write(f"\n{'='*50}")
        self.stdout.write(f"Import complete: {imported_count} imported, {skipped_count} skipped")

    def find_main_html_file(self, folder_path):
        """Find the main HTML file in a folder (not interview or home page files)."""
        html_files = []
        for filename in os.listdir(folder_path):
            if filename.endswith(('.html', '.php')):
                # Skip interview, home page, and blank template files
                lower_name = filename.lower()
                if ('interview' in lower_name or
                    'home' in lower_name or
                    'blank' in lower_name or
                    lower_name.startswith('1_')):
                    continue
                html_files.append(filename)

        # Prefer files ending with _lab.html or _page.php or just .html
        for pattern in ['_lab.html', '_page.php', '_group.html', '.html', '.php']:
            for f in html_files:
                if f.endswith(pattern):
                    return os.path.join(folder_path, f)

        # Return the first one if any exist
        if html_files:
            return os.path.join(folder_path, html_files[0])

        return None

    def extract_tabs(self, html_content):
        """
        Extract tabs from WPBakery shortcode content.

        Looks for pattern:
        [vc_tta_section title="TAB TITLE" tab_id="tab_id"]
        ... content ...
        [/vc_tta_section]
        """
        tabs = []

        # Pattern to match each tab section
        # Handles both single-line and multi-line content
        pattern = r'\[vc_tta_section\s+title="([^"]+)"\s+tab_id="([^"]+)"\s*\](.*?)\[/vc_tta_section\]'

        matches = re.findall(pattern, html_content, re.DOTALL)

        for match in matches:
            title = match[0]
            tab_id = match[1]
            content = match[2].strip()

            # Clean up the content
            content = self.clean_tab_content(content)

            tabs.append({
                'title': title,
                'tab_id': tab_id,
                'content': content,
            })

        return tabs

    def clean_tab_content(self, content):
        """
        Clean up tab content for display.

        - Wraps content in Bootstrap row if needed
        - Fixes image URLs
        - Removes empty elements
        """
        # If content doesn't start with a row wrapper, check if it has columns
        if '<div class="row' not in content and '<div class="col-md-' in content:
            content = f'<div class="row vc-tab-inner">\n{content}\n</div>'

        # Remove any trailing empty paragraphs or divs
        content = re.sub(r'<p>\s*</p>', '', content)
        content = re.sub(r'<div[^>]*>\s*</div>', '', content)

        # Clean up excessive whitespace
        content = re.sub(r'\n\s*\n\s*\n', '\n\n', content)

        return content.strip()
