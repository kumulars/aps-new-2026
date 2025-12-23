"""
Import journal issues from parsed HTML data.
"""
from django.core.management.base import BaseCommand
from home.models import JournalIssue

# Month name to number mapping
MONTH_MAP = {
    'January': 1, 'Jan': 1,
    'February': 2, 'Feb': 2,
    'March': 3,
    'April': 4,
    'May': 5,
    'June': 6,
    'July': 7,
    'August': 8,
    'September': 9, 'Sept': 9,
    'October': 10,
    'November': 11, 'Nov': 11,
    'December': 12,
}

# Journal issues data extracted from WordPress HTML
JOURNAL_ISSUES = [
    # 2025 - Volume 117
    {'volume': 117, 'issue': 6, 'month': 11, 'year': 2025, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2025/117/6'},
    {'volume': 117, 'issue': 5, 'month': 9, 'year': 2025, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2025/117/5'},
    {'volume': 117, 'issue': 4, 'month': 7, 'year': 2025, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2025/117/4'},
    {'volume': 117, 'issue': 3, 'month': 5, 'year': 2025, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2025/117/3'},
    {'volume': 117, 'issue': 2, 'month': 3, 'year': 2025, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2025/117/2'},
    {'volume': 117, 'issue': 1, 'month': 1, 'year': 2025, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2025/117/1'},

    # 2024 - Volume 116
    {'volume': 116, 'issue': 6, 'month': 11, 'year': 2024, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2024/116/6'},
    {'volume': 116, 'issue': 5, 'month': 9, 'year': 2024, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2024/116/5'},
    {'volume': 116, 'issue': 4, 'month': 7, 'year': 2024, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2024/116/4'},
    {'volume': 116, 'issue': 3, 'month': 5, 'year': 2024, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2024/116/3'},
    {'volume': 116, 'issue': 2, 'month': 3, 'year': 2024, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2024/116/2'},
    {'volume': 116, 'issue': 1, 'month': 1, 'year': 2024, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2024/116/1'},

    # 2023 - Volume 115
    {'volume': 115, 'issue': 6, 'month': 11, 'year': 2023, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2023/115/6'},
    {'volume': 115, 'issue': 5, 'month': 9, 'year': 2023, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2023/115/5'},
    {'volume': 115, 'issue': 4, 'month': 7, 'year': 2023, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2023/115/4'},
    {'volume': 115, 'issue': 3, 'month': 5, 'year': 2023, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2023/115/3'},
    {'volume': 115, 'issue': 2, 'month': 3, 'year': 2023, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2023/115/2'},
    {'volume': 115, 'issue': 1, 'month': 1, 'year': 2023, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/115/1'},

    # 2022 - Volume 114
    {'volume': 114, 'issue': 6, 'month': 11, 'year': 2022, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/114/6'},
    {'volume': 114, 'issue': 5, 'month': 9, 'year': 2022, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/114/5'},
    {'volume': 114, 'issue': 4, 'month': 7, 'year': 2022, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/114/4'},
    {'volume': 114, 'issue': 3, 'month': 5, 'year': 2022, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/114/3'},
    {'volume': 114, 'issue': 2, 'month': 3, 'year': 2022, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/114/2'},
    {'volume': 114, 'issue': 1, 'month': 1, 'year': 2022, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2022/114/1'},

    # 2021 - Volume 113
    {'volume': 113, 'issue': 6, 'month': 11, 'year': 2021, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2021/113/6'},
    {'volume': 113, 'issue': 5, 'month': 9, 'year': 2021, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2021/113/5'},
    {'volume': 113, 'issue': 4, 'month': 7, 'year': 2021, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2021/113/4'},
    {'volume': 113, 'issue': 3, 'month': 5, 'year': 2021, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2021/113/3'},
    {'volume': 113, 'issue': 2, 'month': 3, 'year': 2021, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2021/113/2'},
    {'volume': 113, 'issue': 1, 'month': 1, 'year': 2021, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2021/113/1'},

    # 2020 - Volume 112
    {'volume': 112, 'issue': 6, 'month': 11, 'year': 2020, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2020/112/6'},
    {'volume': 112, 'issue': 5, 'month': 9, 'year': 2020, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2020/112/5'},
    {'volume': 112, 'issue': 4, 'month': 7, 'year': 2020, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2020/112/4'},
    {'volume': 112, 'issue': 3, 'month': 5, 'year': 2020, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2020/112/3'},
    {'volume': 112, 'issue': 2, 'month': 3, 'year': 2020, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2020/112/2'},
    {'volume': 112, 'issue': 1, 'month': 1, 'year': 2020, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2020/112/1'},

    # 2019 - Volume 111
    {'volume': 111, 'issue': 6, 'month': 11, 'year': 2019, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2019/111/6'},
    {'volume': 111, 'issue': 5, 'month': 9, 'year': 2019, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2019/111/5'},
    {'volume': 111, 'issue': 4, 'month': 7, 'year': 2019, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2019/111/4'},
    {'volume': 111, 'issue': 3, 'month': 5, 'year': 2019, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2019/111/3'},
    {'volume': 111, 'issue': 2, 'month': 3, 'year': 2019, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2019/111/2'},
    {'volume': 111, 'issue': 1, 'month': 1, 'year': 2019, 'wiley_url': 'https://onlinelibrary.wiley.com/toc/24758817/2019/111/1'},
]


class Command(BaseCommand):
    help = 'Import journal issues for Peptide Science'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be imported without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']

        created_count = 0
        updated_count = 0

        for data in JOURNAL_ISSUES:
            if dry_run:
                self.stdout.write(f"[DRY RUN] Would create: Vol. {data['volume']}, Issue {data['issue']} ({data['year']})")
                continue

            issue, created = JournalIssue.objects.get_or_create(
                volume=data['volume'],
                issue=data['issue'],
                defaults={
                    'month': data['month'],
                    'year': data['year'],
                    'wiley_url': data['wiley_url'],
                }
            )

            if not created:
                # Update existing
                issue.month = data['month']
                issue.year = data['year']
                issue.wiley_url = data['wiley_url']
                issue.save()
                updated_count += 1
                self.stdout.write(f"Updated: Vol. {data['volume']}, Issue {data['issue']}")
            else:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created: Vol. {data['volume']}, Issue {data['issue']} ({data['year']})"))

        if not dry_run:
            self.stdout.write(self.style.SUCCESS(
                f"\nDone! Created {created_count}, updated {updated_count} journal issues."
            ))
