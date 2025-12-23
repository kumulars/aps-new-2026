# APS Website Development Notes

## Project Overview
- **Site**: American Peptide Society (APS) website
- **Platform**: Django/Wagtail
- **Developer**: Lars Sahl (pro bono retirement project)
- **Goal**: Replace WordPress with a stable, expandable, well-structured archive

---

## Production Deployment Procedure

### Server Details
- **Server**: DigitalOcean Droplet `ubuntu-s-2vcpu-4gb-amd-nyc3-01`
- **IP Address**: 159.203.115.118
- **Web Root**: `/var/www/aps2026`
- **Media Storage**: DigitalOcean Spaces bucket `aps2026-production`
- **GitHub Repo**: https://github.com/kumulars/aps-new-2026.git

### One-Time Server Setup (Already Done)
The `.env` file at `/var/www/aps2026/.env` must contain:
```bash
SECRET_KEY=<generated-secret-key>
ALLOWED_HOSTS=americanpeptidesociety.org,www.americanpeptidesociety.org
DB_NAME=aps_wagtail_2026
DB_USER=<database-user>
DB_PASSWORD=<database-password>
DB_HOST=localhost
DB_PORT=5432
SPACES_ACCESS_KEY=<spaces-access-key>
SPACES_SECRET_KEY=<spaces-secret-key>
SPACES_BUCKET_NAME=aps2026-production
SPACES_REGION=nyc3
WAGTAILADMIN_BASE_URL=https://americanpeptidesociety.org
```

The gunicorn service at `/etc/systemd/system/gunicorn.service` must include:
```ini
[Service]
EnvironmentFile=/var/www/aps2026/.env
```
After editing, run: `sudo systemctl daemon-reload`

### Standard Deployment (Code + Database)

#### Step 1: Push Code to GitHub (from Mac)
```bash
cd /Users/larssahl/Documents/wagtail/aps-new-2026
git add -A
git commit -m "Your commit message"
git push origin main
```

#### Step 2: Export Database (from Mac)
```bash
cd /Users/larssahl/Documents/wagtail/aps-new-2026
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude=contenttypes --exclude=auth.permission \
  --exclude=wagtailcore.groupcollectionpermission \
  --exclude=wagtailcore.grouppagepermission \
  --exclude=sessions --indent=2 > db_export_full.json
```

#### Step 3: Transfer Database to Server (from Mac)
```bash
scp /Users/larssahl/Documents/wagtail/aps-new-2026/db_export_full.json \
  root@159.203.115.118:/var/www/aps2026/
```

#### Step 4: Deploy on Server (SSH to server)
```bash
ssh root@159.203.115.118
cd /var/www/aps2026
source venv/bin/activate

# Pull latest code
git pull origin main

# Install any new requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Load database (replaces all data)
python manage.py flush --no-input
python manage.py loaddata /var/www/aps2026/db_export_full.json

# Collect static files
python manage.py collectstatic --no-input

# Restart services
sudo systemctl restart gunicorn
```

### Code-Only Deployment (No Database Changes)
```bash
ssh root@159.203.115.118
cd /var/www/aps2026
source venv/bin/activate
git pull origin main
pip install -r requirements.txt
python manage.py migrate
python manage.py collectstatic --no-input
sudo systemctl restart gunicorn
```

### Troubleshooting

#### 502 Bad Gateway
Check gunicorn status and logs:
```bash
sudo systemctl status gunicorn
sudo journalctl -u gunicorn -n 50 --no-pager
```

Common causes:
- Missing `.env` file or environment variables
- Python/Django errors (check logs)
- Socket permissions issues

#### Environment Variables Not Loading
Ensure `/etc/systemd/system/gunicorn.service` has:
```ini
EnvironmentFile=/var/www/aps2026/.env
```
Then: `sudo systemctl daemon-reload && sudo systemctl restart gunicorn`

---

## FUTURE FEATURE: Research Item Publication Workflow

### Current Manual Workflow
1. Create research item adaptation with images
2. Open HTML in browser, copy article
3. Email PI for approval (template below)
4. Wait for response, enter in CMS
5. Publish and email PI with URLs (template below)
6. Manually post to LinkedIn (and dormant X/Facebook)

### Proposed Automated Workflow

#### Phase 1: Draft Preview System
- [ ] Use Wagtail's built-in draft/publish workflow
- [ ] Create "Share for Review" functionality with unique preview URLs
- [ ] Preview URLs should be:
  - Unpublished/hidden from public
  - Time-limited or token-based
  - Optionally tied to membership system

#### Phase 2: Email Integration
- [ ] Set up self-hosted email on APS server
- [ ] Configure Django SMTP backend to use APS email
- [ ] Create email templates stored in database (editable via admin)
- [ ] Add custom admin actions/buttons:
  - "Send for PI Approval" button on Research Item edit page
  - "Send Publication Notification" button after publishing
- [ ] Email templates with merge fields:
  - `{{ pi_first_name }}`
  - `{{ journal_name }}`
  - `{{ article_url }}`
  - `{{ preview_url }}`

##### Pre-Publication Email Template
```
Subject: APS Research Highlight - Request for Approval

Dear {{ pi_first_name }},

Would you kindly read the below adaptation of your recent publication in
{{ journal_name }} and let me know that it accurately represents your science
and gives appropriate credit to your team? If approved, I want to publish
this on the APS website.

Should you want to highlight any of your authors, please send me a portrait
and a short bio.

[ARTICLE CONTENT OR PREVIEW LINK]

Best regards,
American Peptide Society
```

##### Post-Publication Email Template
```
Subject: Your Research is Now Featured on APS

Dear {{ pi_first_name }},

Thank you for your help in highlighting your work to our audience. I have
published your material at the following URLs. Please let me know that this
all meets with your approval.

{{ site_url }}
{{ article_url }}
{{ archive_url }}
{{ linkedin_url }}
{{ twitter_url }}
{{ facebook_url }}

Best regards,
American Peptide Society
```

#### Phase 3: Social Media Automation
- [ ] Register LinkedIn App (requires company page admin access)
- [ ] Register Twitter/X Developer Account
- [ ] Register Facebook/Meta App
- [ ] Create SocialPost model to track posts across platforms
- [ ] Add "Post to Social Media" admin action with options:
  - Select platforms (LinkedIn, X, Facebook)
  - Preview post content
  - Schedule or post immediately
- [ ] Auto-generate post content from Research Item fields:
  - Short title
  - Lab name
  - Blurb
  - Main image
  - Article URL

### Technical Implementation Notes

#### Email Setup
```python
# settings.py
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.americanpeptidesociety.org'  # or configured server
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'research@americanpeptidesociety.org'
EMAIL_HOST_PASSWORD = env('EMAIL_PASSWORD')
```

#### New Models Needed
```python
class EmailTemplate(models.Model):
    name = models.CharField(max_length=100)  # e.g., "PI Approval Request"
    subject = models.CharField(max_length=200)
    body = models.TextField()  # Supports {{ merge_fields }}

class ResearchItemEmail(models.Model):
    research_item = models.ForeignKey(ResearchItem, ...)
    template_used = models.ForeignKey(EmailTemplate, ...)
    recipient_email = models.EmailField()
    sent_at = models.DateTimeField()

class SocialPost(models.Model):
    research_item = models.ForeignKey(ResearchItem, ...)
    platform = models.CharField(choices=['linkedin', 'twitter', 'facebook'])
    post_url = models.URLField(blank=True)
    posted_at = models.DateTimeField(null=True)
    status = models.CharField(choices=['draft', 'posted', 'failed'])
```

#### Libraries to Consider
- `django-post-office` - Email queue management
- `python-linkedin-v2` or direct API - LinkedIn posting
- `tweepy` - Twitter/X API
- `facebook-sdk` - Facebook API

### Implementation Priority
1. **High**: Draft preview URLs (enables approval workflow)
2. **High**: Email templates + send buttons in admin
3. **Medium**: Self-hosted email setup
4. **Medium**: LinkedIn automation (most active platform, free API)
5. **Low**: Facebook automation (free API, currently dormant)
6. **Skipped**: X/Twitter - API costs $100/month, not worth it for dormant account

---

## Completed Features

### Awards Section (December 2024)
- Award types: Merrifield, du Vigneaud, Goodman, Makineni, Early Career, Hirschmann
- Award recipients with photos and biographies
- Inline image support for bios (lab photos, historical images)
- Admin HelpPanel with copyable inline image template

### Research Items
- Full article management with images
- PI information
- Author spotlights (up to 3)
- Publication metadata

---

## Final Duties

### Cookiebot Integration (Pending)
**Purpose**: Replace WordPress Complianz plugin with Cookiebot for GDPR/CCPA cookie consent

**Plan**: Cookiebot Premium Small ($16/month, up to 350 subpages)

**Current Tracking**: GA4 only (Measurement ID: `GT-NSLFK39S`) - no other pixels

**Implementation Steps**:
1. [ ] Purchase Cookiebot Premium Small for `americanpeptidesociety.org`
2. [ ] Get Cookiebot Domain ID (UUID) from dashboard
3. [ ] Add `COOKIEBOT_ID` to production `.env` file
4. [ ] Add `COOKIEBOT_ENABLED=True` to production `.env` file
5. [ ] Update `base.html` to include Cookiebot script (conditional on environment)
6. [ ] Configure GA4 to use Cookiebot consent signals
7. [ ] Customize banner styling to match APS branding (optional)
8. [ ] Test consent flow on production

**Environment Configuration**:
```python
# settings.py
COOKIEBOT_ID = env('COOKIEBOT_ID', default='')
COOKIEBOT_ENABLED = env.bool('COOKIEBOT_ENABLED', default=False)
```

**Template Integration** (for `base.html`):
```html
{% if cookiebot_enabled and cookiebot_id %}
<script id="Cookiebot" src="https://consent.cookiebot.com/uc.js"
  data-cbid="{{ cookiebot_id }}"
  data-blockingmode="auto"
  type="text/javascript"></script>
{% endif %}
```

### Google Analytics Integration (Pending)
**Purpose**: Connect Wagtail site to existing GA4 property

**Existing Property**: Measurement ID `GT-NSLFK39S`

**Implementation Steps**:
1. [ ] Complete Cookiebot setup first (GA4 depends on consent signals)
2. [ ] Add GA4 tracking code to `base.html` (after Cookiebot script)
3. [ ] Configure for Consent Mode v2 compatibility
4. [ ] Deploy to production
5. [ ] Verify data flowing in GA4 dashboard (may take 24-48 hours)
6. [ ] Confirm real-time view shows visitors

**Template Integration** (for `base.html`, after Cookiebot):
```html
<!-- Google Analytics GA4 with Consent Mode -->
<script async src="https://www.googletagmanager.com/gtag/js?id=GT-NSLFK39S"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}

  // Default consent state (denied until user consents via Cookiebot)
  gtag('consent', 'default', {
    'analytics_storage': 'denied',
    'ad_storage': 'denied',
    'wait_for_update': 500
  });

  gtag('js', new Date());
  gtag('config', 'GT-NSLFK39S');
</script>
```

**Note**: Cookiebot automatically updates consent state when user accepts cookies - no additional code needed for that handoff.

### URL Redirects from WordPress (Pending)
**Purpose**: Redirect old WordPress URLs to new Wagtail URLs to preserve SEO and prevent broken links

**WordPress URL Inventory** (from sitemap analysis):
| Content Type | WordPress Pattern | Wagtail Pattern | Count |
|--------------|-------------------|-----------------|-------|
| Award recipients | `/award/[name]/` | `/awards/recipient/[slug]/` | ~126 |
| Obituaries | `/obituary/[slug]/` | `/people/in-memoriam/[slug]/` | 18 |
| Lab of Month | `/lab-of-the-month/[slug]/` | `/research/[slug]/` | 11 |
| News/Research | `/aps-news/[slug]/` | `/research/[slug]/` | 227 |
| Journal issues | `/journal/vol-X-issue-Y-month/` | `/journal/recent-issues/` | 36 |
| Student highlights | `/student-highlight/[name]/` | `/students/[slug]/` | ~5 |
| Proceedings | `/proceedings-archive/` | `/proceedings/` | 1 |
| Pages | Various | Various (check individually) | ~65 |

**Existing Infrastructure**:
- `InMemoriamProfile` model has `old_url_slug` field for storing WordPress slugs
- Wagtail has built-in redirect management at `/admin/redirects/`

**Implementation Steps**:
1. [ ] Populate `old_url_slug` fields for In Memoriam profiles
2. [ ] Add `old_url_slug` field to other models (AwardRecipient, ResearchItem, etc.)
3. [ ] Create management command to auto-generate redirects from old_url_slug fields
4. [ ] Export WordPress URLs to CSV for reference
5. [ ] Generate redirect mappings (old URL → new URL)
6. [ ] Import redirects via Wagtail admin or management command
7. [ ] Test critical URLs post-deployment
8. [ ] Monitor 404 logs for missed redirects

**Option A: Manual via Wagtail Admin**
Navigate to `/admin/redirects/` and add redirects one by one or import CSV.

**Option B: Management Command (Recommended)**
Create `home/management/commands/generate_redirects.py`:
```python
from django.core.management.base import BaseCommand
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Site
from home.models import AwardRecipient, InMemoriamProfile, ResearchItem

class Command(BaseCommand):
    help = 'Generate redirects from old WordPress URLs'

    def handle(self, *args, **options):
        site = Site.objects.get(is_default_site=True)

        # Award recipients: /award/[old-slug]/ → /awards/recipient/[new-slug]/
        for recipient in AwardRecipient.objects.exclude(old_url_slug=''):
            Redirect.objects.get_or_create(
                old_path=f'/award/{recipient.old_url_slug}/',
                defaults={
                    'redirect_link': f'/awards/recipient/{recipient.slug}/',
                    'is_permanent': True,
                    'site': site,
                }
            )

        # In Memoriam: /obituary/[old-slug]/ → /people/in-memoriam/[new-slug]/
        for profile in InMemoriamProfile.objects.exclude(old_url_slug=''):
            Redirect.objects.get_or_create(
                old_path=f'/obituary/{profile.old_url_slug}/',
                defaults={
                    'redirect_link': f'/people/in-memoriam/{profile.slug}/',
                    'is_permanent': True,
                    'site': site,
                }
            )

        # Add similar blocks for ResearchItem, StudentSpotlight, etc.

        self.stdout.write(self.style.SUCCESS('Redirects generated successfully'))
```

**Static Page Redirects** (add manually):
```
/home/about-us/ → /about/
/proceedings-archive/ → /proceedings/
/featured-labs/ → /research/
/aps-journal/ → /journal/
/aps-journal/recent-journal-issues/ → /journal/recent-issues/
```

**Testing Checklist**:
- [ ] Test 5-10 award recipient redirects
- [ ] Test all In Memoriam redirects
- [ ] Test research item redirects
- [ ] Test main navigation pages
- [ ] Check Google Search Console for 404 errors after launch

### robots.txt (Pending)
**Purpose**: Tell search engines what to crawl and where to find the sitemap

**Implementation**:
Add to `aps_site/urls.py`:
```python
from django.views.generic import TemplateView

urlpatterns = [
    # ... existing patterns ...
    path('robots.txt', TemplateView.as_view(
        template_name='robots.txt',
        content_type='text/plain'
    )),
]
```

Create `aps_site/templates/robots.txt`:
```
User-agent: *
Allow: /

Sitemap: https://americanpeptidesociety.org/sitemap.xml
```

### XML Sitemap (Pending)
**Purpose**: Help search engines discover and index all pages

**Implementation Steps**:
1. [ ] Add `wagtail.contrib.sitemaps` to `INSTALLED_APPS` in `base.py`
2. [ ] Add sitemap URL to `urls.py`:
```python
from wagtail.contrib.sitemaps.views import sitemap

urlpatterns = [
    # ... existing patterns ...
    path('sitemap.xml', sitemap),
]
```
3. [ ] Test at `https://americanpeptidesociety.org/sitemap.xml`
4. [ ] Submit sitemap URL to Google Search Console

### Open Graph Meta Tags (Pending)
**Purpose**: Better previews when links are shared on LinkedIn, Facebook, Twitter

**Implementation**:
Add to `base.html` `<head>` section:
```html
<!-- Open Graph / Social Media -->
<meta property="og:type" content="website">
<meta property="og:site_name" content="American Peptide Society">
<meta property="og:title" content="{% block og_title %}{{ page.title }} - American Peptide Society{% endblock %}">
<meta property="og:description" content="{% block og_description %}{% if page.search_description %}{{ page.search_description }}{% else %}The American Peptide Society promotes research and education in peptide science.{% endif %}{% endblock %}">
<meta property="og:image" content="{% block og_image %}/media/original_images/aps_logo_official.png{% endblock %}">
<meta property="og:url" content="{{ request.build_absolute_uri }}">

<!-- Twitter Card -->
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{% block twitter_title %}{{ page.title }} - American Peptide Society{% endblock %}">
<meta name="twitter:description" content="{% block twitter_description %}{% if page.search_description %}{{ page.search_description }}{% endif %}{% endblock %}">
```

**For Research Items**: Override `og_image` block to use the research item's main image for better social sharing.

### 500 Error Page (Pending)
**Purpose**: Show a friendly error page when something crashes instead of Django's debug page

**Implementation**:
Create `aps_site/templates/500.html`:
```html
{% extends "base.html" %}

{% block title %}Server Error{% endblock %}

{% block body_class %}template-500{% endblock %}

{% block content %}
<div class="container py-5">
    <h1>Something went wrong</h1>
    <p>We're sorry, but something went wrong on our end. Please try again later.</p>
    <p><a href="/">Return to homepage</a></p>
</div>
{% endblock %}
```

### Backup Strategy (Pending)
**Purpose**: Protect against data loss

**Recommended Approach**:
1. [ ] **Database backups**: Set up automated PostgreSQL backups on DigitalOcean
   - DigitalOcean Managed Databases include automatic daily backups
   - Or use cron job: `pg_dump aps_wagtail_2026 > /backups/db_$(date +%Y%m%d).sql`

2. [ ] **Media backups**: DigitalOcean Spaces (already in use) has versioning option
   - Enable versioning in Spaces settings for automatic file history

3. [ ] **Code backups**: Already on GitHub

**Manual Backup Command** (run periodically):
```bash
# On server
cd /var/www/aps2026
source venv/bin/activate
python manage.py dumpdata --natural-foreign --natural-primary \
  --exclude=contenttypes --exclude=auth.permission \
  --exclude=sessions --indent=2 > /backups/db_backup_$(date +%Y%m%d).json
```

### Uptime Monitoring (Pending)
**Purpose**: Get alerted when the site goes down

**Free Options**:
- **UptimeRobot** (free tier): 50 monitors, 5-minute checks
- **Freshping** (free tier): 50 monitors, 1-minute checks
- **Pingdom** (free tier limited)

**Setup**:
1. [ ] Create account at uptimerobot.com
2. [ ] Add monitor for `https://americanpeptidesociety.org`
3. [ ] Configure email alerts
4. [ ] Optionally add monitor for `/admin/` login page

### Link Checker (Pending)
**Purpose**: Verify all internal and external links are working before launch

**Tools**:
- **linkchecker** (Python): `pip install linkchecker`
- **broken-link-checker** (Node.js): `npx broken-link-checker`
- **Screaming Frog SEO Spider** (GUI, free up to 500 URLs)

**Run Locally**:
```bash
# Install linkchecker
pip install linkchecker

# Run against local dev server (start server first)
linkchecker http://127.0.0.1:8000/ --check-extern --no-robots

# Output to file
linkchecker http://127.0.0.1:8000/ --check-extern --no-robots -o html > link_report.html
```

**Run Against Production**:
```bash
linkchecker https://americanpeptidesociety.org/ --check-extern --no-robots
```

**Implementation Steps**:
1. [ ] Run link checker against local dev site
2. [ ] Fix any broken internal links
3. [ ] Note external links that are broken (may need content updates)
4. [ ] Re-run after fixes to confirm
5. [ ] Run against production after deployment

**Common Issues to Watch For**:
- Old WordPress URLs not yet redirected
- External sites that have moved or gone offline
- Typos in manually entered URLs
- Missing trailing slashes

### Accessibility & Responsiveness Audit (Pending)
**Purpose**: Ensure site is accessible to users with disabilities and works across all devices

#### Accessibility Testing

**Tools**:
- **WAVE** (web): https://wave.webaim.org/ - free browser extension and online checker
- **axe DevTools** (browser extension): Chrome/Firefox extension for in-depth audits
- **Lighthouse** (built into Chrome DevTools): Accessibility score and recommendations
- **Pa11y** (CLI): `npx pa11y https://americanpeptidesociety.org/`

**Run Lighthouse Audit**:
1. Open Chrome DevTools (F12)
2. Go to "Lighthouse" tab
3. Check "Accessibility" category
4. Click "Analyze page load"

**WCAG 2.1 Checklist**:
- [ ] All images have meaningful alt text
- [ ] Color contrast meets AA standard (4.5:1 for normal text)
- [ ] Forms have proper labels
- [ ] Keyboard navigation works (Tab through all interactive elements)
- [ ] Skip links present for screen readers
- [ ] Headings are hierarchical (h1 → h2 → h3)
- [ ] Links have descriptive text (not "click here")

#### Responsiveness Testing

**Tools**:
- **Chrome DevTools Device Mode**: Toggle device toolbar (Ctrl+Shift+M)
- **Responsively App** (free): https://responsively.app/ - view multiple sizes simultaneously
- **BrowserStack** (paid): Real device testing

**Breakpoints to Test**:
- Mobile: 375px (iPhone SE), 390px (iPhone 12/13/14)
- Tablet: 768px (iPad), 1024px (iPad Pro)
- Desktop: 1280px, 1440px, 1920px

**Responsiveness Checklist**:
- [ ] Navigation collapses to hamburger menu on mobile
- [ ] Images scale properly (no horizontal scroll)
- [ ] Text is readable without zooming on mobile
- [ ] Touch targets are at least 44x44px
- [ ] Tables scroll horizontally or reflow on mobile
- [ ] Forms are usable on mobile

**Implementation Steps**:
1. [ ] Run Lighthouse accessibility audit on 5 key pages (home, about, awards, research, peptide-links)
2. [ ] Fix critical accessibility issues (score target: 90+)
3. [ ] Test keyboard navigation through main user flows
4. [ ] Test on actual mobile device (not just emulator)
5. [ ] Fix any responsive layout issues
6. [ ] Re-run audits to confirm fixes

---

### Research Item Publication Workflow (Pending)
**Purpose**: Streamline PI communication and social media posting from Wagtail admin

**Full documentation**: See "FUTURE FEATURE: Research Item Publication Workflow" section above (lines 131-267)

**Summary of Components**:

#### Phase 1: PI Email Communication
- [ ] Set up self-hosted email on APS server (or use transactional email service like SendGrid/Mailgun)
- [ ] Configure Django SMTP backend
- [ ] Create `EmailTemplate` model for editable templates in admin
- [ ] Add "Send for PI Approval" button on Research Item edit page
- [ ] Add "Send Publication Notification" button after publishing
- [ ] Create `ResearchItemEmail` model to log sent emails

**Quick Start Option** (simpler than self-hosted):
```python
# settings/production.py - using SendGrid
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.sendgrid.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'apikey'
EMAIL_HOST_PASSWORD = env('SENDGRID_API_KEY')
DEFAULT_FROM_EMAIL = 'research@americanpeptidesociety.org'
```

#### Phase 2: LinkedIn Integration
- [ ] Register LinkedIn App (requires APS company page admin access)
- [ ] Get API credentials (Client ID, Client Secret)
- [ ] Implement OAuth flow for authentication
- [ ] Create `SocialPost` model to track posts
- [ ] Add "Post to LinkedIn" button on Research Item edit page
- [ ] Auto-generate post content from Research Item fields

**LinkedIn API Notes**:
- Free tier allows posting to company pages
- Requires: App registration at linkedin.com/developers
- Scopes needed: `w_organization_social` for company page posting
- Posts can include: text, image, article URL

#### Admin UI Enhancements Needed
Add to Research Item admin panel:
```python
# In ResearchItem model panels
panels = [
    # ... existing panels ...
    MultiFieldPanel([
        FieldPanel('pi_email'),
        ReadOnlyPanel('last_pi_email_sent'),  # Display only
        ReadOnlyPanel('pi_approval_status'),  # Display only
    ], heading="PI Communication"),
    MultiFieldPanel([
        ReadOnlyPanel('linkedin_post_url'),
        ReadOnlyPanel('linkedin_posted_at'),
    ], heading="Social Media"),
]
```

**Implementation Priority**:
1. Email templates + send buttons (High - enables approval workflow)
2. LinkedIn posting (Medium - most active social platform)
3. Facebook/X automation (Low - currently dormant accounts)

### Researcher Profile Update Campaign (Pending)
**Purpose**: Populate research areas and verify researcher data via self-service form

**Background**:
- 420 researchers in PeptideLinks directory
- 345 have NO research area assigned
- 2 research areas have 0 researchers (Peptide Chemistry, Therapeutic Peptides)
- Data needs to be verified/updated by the researchers themselves

**Two Taxonomies to Consolidate**:
| ResearchArea (Peptide Links) | ResearchItemCategory (Research Items) |
|------------------------------|---------------------------------------|
| 12 categories | 11 categories |
| Broad disciplines | Specific topics |
| Only 2 overlap | - |

**Implementation Steps**:
1. [ ] Decide on unified taxonomy (merge or keep separate)
2. [ ] Create public researcher update form:
   - Token-based URL (unique per researcher) OR
   - Email verification to edit
   - Fields: name, institution, website, ORCID, PubMed, Google Scholar, research areas (multi-select)
3. [ ] Build form view and template
4. [ ] Set up email campaign infrastructure
5. [ ] Compose email asking researchers to verify/update their profile
6. [ ] Send campaign to all 420 researchers
7. [ ] Monitor responses and follow up

**Form Options**:
- **Option A: Token-based** - Each researcher gets unique URL like `/update-profile/<token>/`
- **Option B: Email verification** - Researcher enters email, receives link to edit

**Email Template Draft**:
```
Subject: Please Update Your PeptideLinks Directory Profile

Dear [Name],

The American Peptide Society maintains the PeptideLinks Directory at
americanpeptidesociety.org/peptide-links/

We would like to ensure your profile is accurate and complete. Please take
a moment to verify your information and add your research areas:

[UPDATE LINK]

This helps students and collaborators find researchers in specific areas
of peptide science.

Best regards,
American Peptide Society
```

### Symposium Image Galleries - Broken on Production (Pending)
**Issue**: Image connections lost on production site. The SymposiumImage model references Wagtail Image objects via ForeignKey, but the image relationships are broken after deployment.

**Affected Years**: 2015, 2017, 2019, 2022, 2023, 2025

**Location**:
- Model: `home/models.py` - SymposiumGalleryPage (line ~607)
- Template: `home/templates/home/symposium_gallery_page.html`
- Images referenced via: `{% image img.image fill-250x167 %}`

**Likely Causes**:
1. Image ForeignKey IDs in database don't match Image objects in production
2. Images not uploaded to DigitalOcean Spaces
3. SymposiumImage records exist but point to non-existent Image IDs

**To Diagnose** (run on production):
```bash
cd /var/www/aps2026
source venv/bin/activate
python manage.py shell

# Check if SymposiumImage records exist
from home.models import SymposiumImage
print(f"Total SymposiumImage records: {SymposiumImage.objects.count()}")

# Check for broken image references
for img in SymposiumImage.objects.all()[:10]:
    try:
        print(f"Year {img.year}: {img.image.title} - OK")
    except:
        print(f"Year {img.year}: BROKEN - image_id={img.image_id}")
```

**To Fix**:
- [ ] Diagnose which images are missing vs which have broken FK references
- [ ] Re-upload symposium images to DigitalOcean Spaces if missing
- [ ] Re-run import command if needed: `python manage.py import_symposium_images`
- [ ] Or manually re-link images in Wagtail admin

---

## Notes
- Inline image HTML format for bios:
```html
<div style="margin: 29px">
<img src="/media/original_images/FILENAME.jpg" alt="DESCRIPTION" style="margin-bottom: 19px;" class="img-fluid">
<p class="small">CAPTION TEXT</p>
</div>
```
