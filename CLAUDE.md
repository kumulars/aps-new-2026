# APS Website Development Notes

## Project Overview
- **Site**: American Peptide Society (APS) website
- **Platform**: Django/Wagtail
- **Developer**: Lars Sahl (pro bono retirement project)
- **Goal**: Replace WordPress with a stable, expandable, well-structured archive

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

## Notes
- Inline image HTML format for bios:
```html
<div style="margin: 29px">
<img src="/media/original_images/FILENAME.jpg" alt="DESCRIPTION" style="margin-bottom: 19px;" class="img-fluid">
<p class="small">CAPTION TEXT</p>
</div>
```
