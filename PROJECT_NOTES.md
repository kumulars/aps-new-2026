# APS Website Rebuild - Project Notes
**Last Updated:** December 16, 2025

## Project Overview
Rebuilding the American Peptide Society website from WordPress to Django/Wagtail.

**Project Location:** `/Users/larssahl/documents/wagtail/aps-new-2026/`
**Old WordPress Data:** `/Users/larssahl/documents/wagtail/aps2026/`

---

## Completed Sections

### 1. Homepage & Research Items
- Homepage displays latest research items in flexbox grid
- Research items are snippets with full article content
- Archive page at `/news/` with category filtering
- Detail pages at `/news/<slug>/`

### 2. Symposium Gallery (`/symposium-images/`)
- **Layout:** 2+10 columns (sidebar + main content)
- Years: 2015 (Orlando), 2017 (Whistler), 2019 (Monterey), 2022 (Whistler), 2023 (Tucson), 2025 (San Diego)
- Sidebar navigation becomes horizontal scrollable on mobile
- Each year has banner, two-column description, and image gallery

**Key Files:**
- Model: `home/models.py` - `SymposiumImage`, `SymposiumGalleryPage`
- Template: `home/templates/home/symposium_gallery_page.html`
- CSS: `aps_site/static/css/symposium.css`

### 3. PeptideLinks Directory (`/peptide-links/`)
- **Layout:** Sidebar filters + main researcher grid
- 426 researchers imported from peptidelinks.net
- Filtering by country, state, research area, alphabetical
- Name cards with links to website, ORCID, PubMed, Google Scholar
- Button opacity: 70%, white icons on hover

**Key Files:**
- Model: `home/models.py` - `Researcher`, `ResearchArea`, `PeptideLinksIndexPage`
- Template: `home/templates/home/peptide_links_index_page.html`
- CSS: `aps_site/static/css/peptidelinks.css`

### 4. People Section (`/people/`)
- **Layout:** 2+10 columns (sidebar + main content)
- Three views: Officers & Councilors, Past Presidents, Committees
- Sidebar navigation (no icons, just text labels)

**Current Officers (2025-2027 term):**
- President: Anna Mapp
- President-Elect: James S. Nowick
- Secretary: Anna Maria Papini
- Treasurer: Carrie Haskell-Luevano
- Immediate Past President: Joel Schneider

**Councilors:** 11 current members including Champak Chatterjee, Betsy Parkinson, Alanna Schepartz, Jenn Stockdill, Wilfred van der Donk

**Past Presidents:** 16 imported (1994-2023)

**Staff:** Lars Sahl (Web Developer)

**Photo dimensions:** 140x170px rectangular with 6px border-radius

**Key Files:**
- Models: `home/models.py` - `APSRole`, `APSCommittee`, `APSPerson`, `PersonRoleAssignment`, `PersonCommitteeMembership`, `PeopleIndexPage`
- Template: `home/templates/home/people_index_page.html`
- CSS: `aps_site/static/css/people.css`
- Import command: `home/management/commands/import_people.py`

### 5. Awards System (`/awards/`)
- **Layout:** 2+6+4 columns (nav sidebar + main content + sponsor/image column)
- 6 award types in order of significance:
  1. R. Bruce Merrifield Award
  2. Vincent du Vigneaud Award
  3. Murray Goodman Scientific Excellence & Mentorship Award
  4. Rao Makineni Lectureship
  5. APS Early Career Investigator Lectureship
  6. Ralph F. Hirschmann Award

**Index Page (`/awards/?award=merrifield`):**
- Left column: Award type navigation buttons
- Center column: Award title, description, recipients grouped by decade
- Right column: Sponsor logo/image and description
- Recipients listed with year, clickable name, institution
- Small photos (60x75px) also clickable

**Detail Pages (`/awards/recipient/<slug>/`):**
- Same 2+6+4 layout
- Breadcrumb back to award list
- Full biography with proper paragraph formatting
- Large photo in right column (or placeholder)

**Data:**
- 124 total recipients imported from CSV
- 49 biographies with proper paragraph formatting
- 32 recipients have photos linked from Wagtail image library
- Auto-generated slugs (e.g., `philip-e-dawson-2025`)

**Merrifield Award Special:**
- Bruce Merrifield image in right column (ID 1781)
- Caption about Merrifield's contributions

**Key Files:**
- Models: `home/models.py` - `AwardType`, `AwardRecipient`, `AwardsIndexPage`
- View: `home/views.py` - `award_recipient_detail()`
- URL: `aps_site/urls.py` - `/awards/recipient/<slug>/`
- Templates:
  - `home/templates/home/awards_index_page.html`
  - `home/templates/home/award_recipient_detail.html`
- CSS: `aps_site/static/css/awards.css`
- Import command: `home/management/commands/import_awards.py`

### 6. Global Peptide Groups (`/global-peptide-groups/`)
- **Layout:** Archive page with cards + detail pages with Bootstrap tabs
- Renamed from "Lab of the Month" to "Global Peptide Groups"
- 7 groups imported with full tabbed content from WordPress

**Groups Imported:**
- The Craik Group (November 2025) - CURRENT
- The Sun Group (December 2025)
- The Del Valle Group (September 2025)
- The D'Amelio Group (May 2025)
- The Schmeing Lab (December 2024)
- The David Lab (November 2024)
- The Kiessling Lab (October 2024)

**Features:**
- Tabbed content pages with raw HTML support
- Archive grid with featured group highlight
- Bootstrap tabs with horizontal scroll on mobile
- Redirects from old `/lab-of-the-month/` URLs

**Key Files:**
- Models: `home/models.py` - `TabBlock`, `GlobalPeptideGroupPage`, `GlobalPeptideGroupIndexPage`
- Templates:
  - `home/templates/home/global_peptide_groups_index_page.html`
  - `home/templates/home/global_peptide_group_page.html`
- CSS: `aps_site/static/css/global_peptide_groups.css`
- Import command: `home/management/commands/import_global_peptide_groups.py`

**Not Imported (different format):**
- Liu Lab (April 2025) - flat HTML structure, no tabs
- Kay Group (January 2025) - incomplete content
- Nitsche Lab (September 2024) - no HTML file

### 7. Merrifield Essay Page (`/merrifield-essay/`)
- **Layout:** Single column, centered content
- Static page with Bruce Merrifield's essay on Solid Phase Peptide Synthesis
- Linked from the Merrifield Award section on Awards page
- Full historical essay with proper paragraph formatting

**Key Files:**
- View: `home/views.py` - `merrifield_essay()`
- URL: `aps_site/urls.py` - `/merrifield-essay/`
- Template: `home/templates/home/merrifield_essay.html`

### 8. Student Activities Committee (`/people/student-activities-committee/`)
- **Layout:** Single column, article format
- Information about SAC activities and committee members
- Three SAC photos downloaded from WordPress
- Added to People dropdown navigation

**Key Files:**
- View: `home/views.py` - `student_activities_committee()`
- URL: `aps_site/urls.py` - `/people/student-activities-committee/`
- Template: `home/templates/home/student_activities_committee.html`
- Images: `media/sac/` (SAC-Tucson-2.jpg, SAC-Tucson-3.jpg, sac-welcome.jpg)

### 9. In Memoriam Section (`/people/in-memoriam/`)
- **Layout:** Index page with 4-column card grid, detail pages with photo right
- Tribute pages for departed colleagues in the peptide science community
- 18 entries imported from old aps2026 SQLite database

**Index Page (`/people/in-memoriam/`):**
- 4-column responsive grid (col-sm-6 col-lg-3)
- Portrait photos with 973:1200 aspect ratio (matching original image dimensions)
- Blurb text truncated to 30 words
- "Read tribute" links to detail pages

**Detail Pages (`/people/in-memoriam/<slug>/`):**
- Photo column on right (col-lg-4), content on left (col-lg-8)
- Bootstrap order classes for mobile (photo first, then content)
- Full obituary text with HTML formatting preserved
- Placeholder icon for entries without photos

**Data Model:** `InMemoriam` snippet
- first_name, last_name, slug, photo, blurb, full_text, display_order
- Ordered by display_order descending

**Key Files:**
- Model: `home/models.py` - `InMemoriam`
- Views: `home/views.py` - `in_memoriam_index()`, `in_memoriam_detail()`
- URLs: `aps_site/urls.py`
- Templates:
  - `home/templates/home/in_memoriam_index.html`
  - `home/templates/home/in_memoriam_detail.html`
- CSS: `aps_site/static/css/aps_site.css` (memoriam styles)
- Import source: `/Users/larssahl/documents/wagtail/aps2026/db.sqlite3`

**Migrations for Awards:**
- `0007_awardsindexpage_awardtype_awardrecipient.py` - Initial models
- `0008_awardrecipient_slug.py` - Add slug field
- `0009_populate_recipient_slugs.py` - Generate slugs for existing records
- `0010_awardrecipient_slug_unique.py` - Make slug unique

---

## Design Patterns Used

### Sidebar Navigation
- Sticky on desktop (top: 70px)
- Horizontal scrollable on mobile (<992px)
- Buttons with active state highlighting (blue background)

### Column Layouts
- **2+10:** Symposium, People (sidebar + full content)
- **2+6+4:** Awards (nav + content + sponsor info)

### CSS Variables (defined in base.css)
- `--aps-blue`: Primary blue color
- `--aps-orange`: Accent color (used in section headers)
- `--aps-green`: Secondary accent
- `--aps-link`: Link color
- `--aps-text`: Text color

### Mobile Breakpoints
- `991.98px`: Sidebar becomes horizontal
- `575.98px`: Further mobile adjustments

---

## Database Info

**Development:**
- SQLite database: `db.sqlite3`
- All models registered as Wagtail snippets for admin management
- Images stored in Wagtail image library

**Production:**
- PostgreSQL database: `aps2026` (user: `aps2026user`)
- Server: DigitalOcean droplet `ubuntu-s-2vcpu-4gb-amd-nyc3-01`
- IP: `159.203.115.118`
- Path: `/var/www/aps2026`
- Domain: `americanpeptidesociety.org`

---

## Production Deployment Process

### 1. Push Code to GitHub
```bash
cd /Users/larssahl/documents/wagtail/aps-new-2026
git add -A && git commit -m "Description" && git push
```

### 2. Export Database (on Mac)
```bash
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude contenttypes --exclude auth.permission \
  --exclude admin.logentry --exclude sessions \
  --exclude wagtailcore.modellogentry --exclude wagtailcore.pagelogentry \
  --indent 2 -o /tmp/aps_dump.json
```

### 3. Transfer Files to Production
```bash
# Database dump
scp /tmp/aps_dump.json root@159.203.115.118:/var/www/aps2026/

# Media files
rsync -avz --progress media/ root@159.203.115.118:/var/www/aps2026/media/
```

### 4. On Production Server
```bash
ssh root@159.203.115.118
cd /var/www/aps2026
source venv/bin/activate

# Pull latest code
git pull

# For full database sync (drop and recreate)
systemctl stop gunicorn
sudo -u postgres psql -c "DROP DATABASE aps2026;"
sudo -u postgres psql -c "CREATE DATABASE aps2026 OWNER aps2026user;"
python manage.py migrate
python manage.py loaddata aps_dump.json

# Finish up
python manage.py collectstatic --noinput
systemctl start gunicorn
```

### Important Notes
- Always stop gunicorn before database operations
- The `--natural-foreign --natural-primary` flags are essential for SQLite→PostgreSQL migration
- Excluding `contenttypes` and `auth.permission` prevents ID mismatch errors

---

## Running the Project
```bash
cd /Users/larssahl/documents/wagtail/aps-new-2026
python manage.py runserver
```

**Development URLs:**
- Homepage: http://127.0.0.1:8000/
- Admin: http://127.0.0.1:8000/admin/
- Awards: http://127.0.0.1:8000/awards/
- People: http://127.0.0.1:8000/people/
- Student Activities Committee: http://127.0.0.1:8000/people/student-activities-committee/
- In Memoriam: http://127.0.0.1:8000/people/in-memoriam/
- Symposium Images: http://127.0.0.1:8000/symposium-images/
- PeptideLinks: http://127.0.0.1:8000/peptide-links/
- Global Peptide Groups: http://127.0.0.1:8000/global-peptide-groups/
- Merrifield Essay: http://127.0.0.1:8000/merrifield-essay/

**Production URL:** https://americanpeptidesociety.org/

---

## Potential Next Steps
1. Knowledge Base section (needs fresh approach - original CSV has 76 articles with 43 category tags, no inherent chapter structure)
2. Import more award recipient photos (92 remaining without photos)
3. Add sponsor information for other awards (currently only Merrifield has image)
4. Committee members data entry
5. Additional pages (About, Contact, Membership, etc.)
6. Search functionality
7. Mobile testing and refinements
8. Import remaining Global Peptide Groups (Liu Lab, Kay Group, Nitsche Lab - need manual conversion)

---

## Image IDs Reference (Wagtail)
- Bruce Merrifield: 1781
- Philip Dawson: 1761
- Portrait images range: 1740-1781 (people photos)
- Symposium banners in `symposium_banners/` folder
