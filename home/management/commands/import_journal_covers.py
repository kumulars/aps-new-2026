"""
Download and import journal cover images from WordPress.
"""
import os
import requests
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from home.models import JournalIssue

# Cover image URLs from WordPress (extracted from HTML)
COVER_URLS = {
    # 2025 - Volume 117
    (117, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2025/03/peptide_science_117_2.jpg',
    (117, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2025/03/peptide_science_117_2.jpg',
    (117, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2025/03/peptide_science_117_2.jpg',
    (117, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2025/05/peptide_science_117_3.jpg',
    (117, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2025/03/peptide_science_117_2.jpg',
    (117, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2025/01/peptide_science_117_1.jpg',

    # 2024 - Volume 116
    (116, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2024/11/peptide_science_116_6.jpg',
    (116, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2024/09/peptide_science_116_5.jpg',
    (116, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2024/07/peptide_science_116_4_2.jpg',
    (116, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2024/05/peptide_science_116_3.jpg',
    (116, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2024/03/peptide_science_116_2.jpg',
    (116, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2024/02/peptide_science_116_1.jpg',

    # 2023 - Volume 115
    (115, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_115_5.jpg',
    (115, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_115_5.jpg',
    (115, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_115_4.jpg',
    (115, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_115_3.jpg',
    (115, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_115_2.jpg',
    (115, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2023/02/Pep-Sci-Jan-2023.jpg',

    # 2022 - Volume 114
    (114, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_114_6.jpg',
    (114, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2022/09/Pep-Sci-Sept-2022-e1664229601114.jpg',
    (114, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2022/07/Pep-Sci-July-2022-e1659109230326.jpg',
    (114, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2022/06/Pep-Sci-May-2022-e1655421249707.jpg',
    (114, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2022/03/Pep-Sci-March-2022-e1648338770239.jpg',
    (114, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2022/02/Pep-Sci-Jan-2022-e1644426333775.jpg',

    # 2021 - Volume 113
    (113, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2022/01/Pep-Sci-Nov-2021-e1643210162664.jpg',
    (113, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2021/09/Pep-Sci-Sept-2021-lg-e1632918598934.jpg',
    (113, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2021/07/Pep-Sci-July-2021-large-e1627160338630.jpg',
    (113, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2021/05/Pep-Sci-May-2021-2.jpg',
    (113, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2021/03/113_2_pepsci.jpg',
    (113, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2021/02/Pep-Science-Jan-2021-e1612628708717.jpg',

    # 2020 - Volume 112
    (112, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2020/12/PepSci-cover-Nov-2020-e1606933652787.jpg',
    (112, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2020/09/Pep-Sci-Sept-2020.jpg',
    (112, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_112_4.jpg',
    (112, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2020/06/journal_cover_112_3.jpg',
    (112, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2020/03/journal_cover_112_2.jpg',
    (112, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2020/01/journal_cover_112.jpg',

    # 2019 - Volume 111
    (111, 6): 'https://americanpeptidesociety.org/wp-content/uploads/2019/12/peptide_science_111.jpg',
    (111, 5): 'https://americanpeptidesociety.org/wp-content/uploads/2019/11/volume_111_Issue_5.jpg',
    (111, 4): 'https://americanpeptidesociety.org/wp-content/uploads/2019/07/journal_july.jpg',
    (111, 3): 'https://americanpeptidesociety.org/wp-content/uploads/2019/07/peptide_science.jpg',
    (111, 2): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_111_2.jpg',
    (111, 1): 'https://americanpeptidesociety.org/wp-content/uploads/2023/11/peptide_science_111_1.jpg',
}


class Command(BaseCommand):
    help = 'Download and import journal cover images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        # Track downloaded images to avoid duplicates
        downloaded_images = {}
        success_count = 0
        skip_count = 0
        error_count = 0

        for (volume, issue), url in COVER_URLS.items():
            try:
                journal_issue = JournalIssue.objects.get(volume=volume, issue=issue)
            except JournalIssue.DoesNotExist:
                self.stderr.write(f"Issue not found: Vol. {volume}, Issue {issue}")
                continue

            # Skip if already has cover image
            if journal_issue.cover_image:
                self.stdout.write(f"Skipping Vol. {volume}, Issue {issue} (already has cover)")
                skip_count += 1
                continue

            if dry_run:
                self.stdout.write(f"[DRY RUN] Would download: {url}")
                continue

            # Check if we already downloaded this URL
            if url in downloaded_images:
                journal_issue.cover_image = downloaded_images[url]
                journal_issue.save()
                self.stdout.write(f"Reused image for Vol. {volume}, Issue {issue}")
                success_count += 1
                continue

            # Download the image
            try:
                self.stdout.write(f"Downloading Vol. {volume}, Issue {issue}...")
                response = requests.get(url, timeout=30)
                response.raise_for_status()

                # Get filename from URL
                filename = url.split('/')[-1]
                # Clean up filename
                filename = f"pepsci_vol{volume}_issue{issue}.jpg"

                # Create Wagtail image
                image_file = ImageFile(BytesIO(response.content), name=filename)
                wagtail_image = Image(
                    title=f"Peptide Science Vol. {volume} Issue {issue}",
                    file=image_file,
                )
                wagtail_image.save()

                # Link to journal issue
                journal_issue.cover_image = wagtail_image
                journal_issue.save()

                # Cache for reuse
                downloaded_images[url] = wagtail_image

                self.stdout.write(self.style.SUCCESS(f"Imported Vol. {volume}, Issue {issue}"))
                success_count += 1

            except Exception as e:
                self.stderr.write(f"Error downloading Vol. {volume}, Issue {issue}: {e}")
                error_count += 1

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Imported {success_count}, skipped {skip_count}, errors {error_count}"
            ))
