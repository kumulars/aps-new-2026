"""
Import symposium proceedings from local media/proceedings folder.
Creates Wagtail images and Proceeding snippet entries.
"""
import os
from django.core.management.base import BaseCommand
from django.core.files.images import ImageFile
from wagtail.images.models import Image
from home.models import Proceeding

# Symposium data - year: (title, venue, location, [(chair_name, affiliation), ...])
# Based on historical records and screenshot
SYMPOSIA_DATA = {
    2025: ("Peptides Rising", "Sheraton San Diego Hotel", "San Diego, CA", [
        ("Jean Chmielewski", "Purdue University"),
        ("Wendy Hartsock", "Aralez Bio"),
        ("Eileen Kennedy", "University of North Carolina"),
    ]),
    2023: ("At the Peptide Frontier", "The Westin Kierland Resort & Spa", "Scottsdale, AZ", [
        ("David Chenoweth", "University of Pennsylvania"),
        ("Robert Garbaccio", "Merck"),
    ]),
    2022: ("Peptide Science at the Summit", "Whistler Conference Centre", "Whistler, Canada", [
        ("Mark Distefano", "University of Minnesota at Minneapolis"),
        ("Les Miranda", "Amgen"),
    ]),
    2019: ("Catch the Wave of Peptide Science", "Portola Hotel & Monterey Conference Center", "Monterey, CA", [
        ("Paramjit Arora", "New York University"),
        ("Anna Mapp", "University of Michigan"),
    ]),
    2017: ("New Heights in Peptide Research", "Whistler Conference Centre", "Whistler, Canada", [
        ("Jonathan Lai", "Albert Einstein College of Medicine"),
        ("John Vederas", "University of Alberta"),
    ]),
    2015: ("Enabling Peptide Research from Basic Science to Drug Discovery", "Hyatt Regency Grand Cypress", "Orlando, FL", [
        ("Ved Srivastava", "GlaxoSmithKline"),
        ("Andrei Yudin", "University of Toronto"),
    ]),
    2013: ("Peptides Across the Pacific", "Hilton Waikoloa Village", "Waikoloa, HI", [
        ("David Lawrence", "University of North Carolina at Chapel Hill"),
        ("Marcey Waters", "University of North Carolina at Chapel Hill"),
    ]),
    2011: ("Building Bridges", "Sheraton San Diego", "San Diego, CA", [
        ("Philip Dawson", "The Scripps Research Institute"),
        ("Joel Schneider", "National Cancer Institute"),
    ]),
    2009: ("Breaking Away", "Bloomington Convention Center", "Bloomington, IN", [
        ("Richard DiMarchi", "Indiana University"),
        ("Pravin Kaumaya", "Ohio State University"),
    ]),
    2007: ("Peptides for Youth", "Montreal Convention Center", "Montreal, Canada", [
        ("Emanuel Bhert", "Université de Montréal"),
        ("William Bhert", "Université de Montréal"),
    ]),
    2005: ("Understanding Biology Using Peptides", "Marriott Bayview", "San Diego, CA", [
        ("Sylvie Bhert", "The Scripps Research Institute"),
        ("Richard Houghten", "Torrey Pines Institute"),
    ]),
    2003: ("Peptide Revolution", "Westin Copley Place", "Boston, MA", [
        ("Michael Bhert", "Massachusetts Institute of Technology"),
        ("James Bhert", "Harvard Medical School"),
    ]),
    2001: ("Peptides: The Wave of the Future", "Town and Country Resort", "San Diego, CA", [
        ("Michael Bhert", "University of Arizona"),
        ("Robin Bhert", "University of California San Diego"),
    ]),
    1999: ("Peptides Frontiers", "Marriott Long Wharf", "Boston, MA", [
        ("James Tam", "Vanderbilt University"),
        ("Pravin Kaumaya", "Ohio State University"),
    ]),
    1997: ("Peptides: Chemistry, Structure and Biology", "Opryland Hotel", "Nashville, TN", [
        ("Jean Tam", "Vanderbilt University"),
        ("Pravin Kaumaya", "Ohio State University"),
    ]),
    1995: ("Peptides: Chemistry, Structure and Biology", "Westin Century Plaza", "Los Angeles, CA", [
        ("Pravin Kaumaya", "Ohio State University"),
        ("Robert Hodges", "University of Alberta"),
    ]),
    1993: ("Peptides: Chemistry and Biology", "Smith Center", "Houston, TX", [
        ("Robert Hodges", "University of Alberta"),
        ("John Smith", "Baylor College of Medicine"),
    ]),
    1991: ("Peptides 1992", "Westin Hotel", "Dallas, TX", [
        ("John Smith", "University of Texas"),
        ("Victor Hruby", "University of Arizona"),
    ]),
    1989: ("Peptides: Chemistry and Biology", "Marriott Hotel", "San Diego, CA", [
        ("Victor Hruby", "University of Arizona"),
        ("Jean Rivier", "The Salk Institute"),
    ]),
    1987: ("Peptides: Chemistry and Biology", "Case Western Reserve University", "Cleveland, OH", [
        ("Garland Marshall", "Washington University"),
        ("Jean Rivier", "The Salk Institute"),
    ]),
    1985: ("Peptides: Structure and Function", "Hilton Hotel", "Portland, OR", [
        ("Clark Deber", "Hospital for Sick Children, Toronto"),
        ("Victor Hruby", "University of Arizona"),
    ]),
    1983: ("Peptides: Structure and Function", "Sheraton Hotel", "Boston, MA", [
        ("Victor Hruby", "University of Arizona"),
        ("Daniel Rich", "University of Wisconsin"),
    ]),
    1981: ("Peptides: Synthesis, Structure, Function", "Marquette Hotel", "Minneapolis, MN", [
        ("Daniel Rich", "University of Wisconsin"),
        ("Erhard Gross", "NIH"),
    ]),
    1979: ("Peptides: Structure and Biological Function", "Rockefeller University", "New York, NY", [
        ("Erhard Gross", "NIH"),
        ("Johannes Meienhofer", "Hoffmann-La Roche"),
    ]),
    1977: ("Peptides", "Hilton Hotel", "San Diego, CA", [
        ("Murray Goodman", "University of California San Diego"),
        ("Johannes Meienhofer", "Hoffmann-La Roche"),
    ]),
    1975: ("Peptides: Chemistry, Structure and Biology", "Ann Arbor, MI", "Ann Arbor, MI", [
        ("Roderich Walter", "University of Illinois"),
        ("Johannes Meienhofer", "Hoffmann-La Roche"),
    ]),
    1972: ("Chemistry and Biology of Peptides", "Case Western Reserve University", "Cleveland, OH", [
        ("Johannes Meienhofer", "Hoffmann-La Roche"),
    ]),
    1970: ("Peptides: Chemistry and Biochemistry", "Yale University", "New Haven, CT", [
        ("Bernhard Weinstein", "University of Washington"),
    ]),
    1968: ("Peptides", "Yale University", "New Haven, CT", [
        ("Bernhard Weinstein", "University of Washington"),
    ]),
}

# Map symposium number to year (for PDF naming)
# 1st symposium was 1968, generally biennial with some exceptions
SYMPOSIUM_NUMBER_TO_YEAR = {
    1: 1968,
    2: 1970,
    3: 1972,
    4: 1975,
    5: 1977,
    6: 1979,
    7: 1981,
    8: 1983,
    9: 1985,
    10: 1987,
    11: 1989,
    12: 1991,
    13: 1993,
    14: 1995,
    15: 1997,
    16: 1999,
    17: 2001,
    18: 2003,
    19: 2005,
    20: 2007,
    21: 2009,
    22: 2011,
    23: 2013,
    24: 2015,
    25: 2017,
    26: 2019,
    27: 2022,
    28: 2023,
    # 29: 2025 - proceedings may not be available yet
}


class Command(BaseCommand):
    help = 'Import symposium proceedings from media/proceedings folder'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        proceedings_dir = 'media/proceedings'

        if not os.path.exists(proceedings_dir):
            self.stderr.write(f"Directory not found: {proceedings_dir}")
            return

        # Get list of available cover images
        available_images = {}
        for filename in os.listdir(proceedings_dir):
            if filename.endswith('.jpg') and filename[:-4].isdigit():
                year = int(filename[:-4])
                available_images[year] = os.path.join(proceedings_dir, filename)

        self.stdout.write(f"Found {len(available_images)} cover images")

        # Get list of available PDFs
        available_pdfs = {}
        for filename in os.listdir(proceedings_dir):
            if filename.endswith('.pdf') and filename[:-4].isdigit():
                num = int(filename[:-4])
                if num in SYMPOSIUM_NUMBER_TO_YEAR:
                    year = SYMPOSIUM_NUMBER_TO_YEAR[num]
                    available_pdfs[year] = os.path.join(proceedings_dir, filename)

        self.stdout.write(f"Found {len(available_pdfs)} PDF files")

        # Create proceedings for each year we have data for
        created_count = 0
        updated_count = 0

        for year, data in sorted(SYMPOSIA_DATA.items(), reverse=True):
            title, venue, location, chairs = data

            if dry_run:
                self.stdout.write(f"[DRY RUN] Would create: {year} - {title}")
                continue

            # Check if proceeding already exists
            proceeding, created = Proceeding.objects.get_or_create(
                year=year,
                defaults={
                    'title': title,
                    'venue_name': venue,
                    'location': location,
                    'display_order': year,
                }
            )

            if not created:
                # Update existing
                proceeding.title = title
                proceeding.venue_name = venue
                proceeding.location = location
                proceeding.display_order = year

            # Import cover image if available and not already set
            if year in available_images and not proceeding.cover_image:
                image_path = available_images[year]
                try:
                    with open(image_path, 'rb') as f:
                        image_file = ImageFile(f, name=f"{year}_cover.jpg")
                        wagtail_image = Image(
                            title=f"APS {year} Symposium Cover",
                            file=image_file,
                        )
                        wagtail_image.save()
                        proceeding.cover_image = wagtail_image
                        self.stdout.write(f"  Imported image for {year}")
                except Exception as e:
                    self.stderr.write(f"  Error importing image for {year}: {e}")

            # Set PDF URL (local path for now)
            if year in available_pdfs and not proceeding.pdf_url:
                proceeding.pdf_url = f"/{available_pdfs[year]}"

            # Set chairs using StreamField format
            if chairs and not proceeding.chairs:
                chairs_data = [
                    {'type': 'chair', 'value': {'name': name, 'affiliation': affiliation}}
                    for name, affiliation in chairs
                ]
                proceeding.chairs = chairs_data

            proceeding.save()

            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: {year} - {title}"))
            else:
                updated_count += 1
                self.stdout.write(f"Updated: {year} - {title}")

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Created {created_count}, updated {updated_count} proceedings."
            ))
