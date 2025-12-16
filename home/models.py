from django.db import models
from django.utils import timezone
from django.utils.text import slugify
from django.urls import reverse

from wagtail.models import Page
# Note: We use TextField (not RichTextField) for body content
# because we need to paste raw HTML with inline styles, classes, etc.
from wagtail.admin.panels import FieldPanel, MultiFieldPanel, InlinePanel
from wagtail.snippets.models import register_snippet
from wagtail.fields import StreamField
from wagtail.blocks import StructBlock, CharBlock, TextBlock
from wagtail.images.blocks import ImageChooserBlock
from modelcluster.models import ClusterableModel
from modelcluster.fields import ParentalKey


class HomePage(Page):
    """
    Homepage displaying latest research items in a flexbox grid.
    """

    def get_context(self, request):
        context = super().get_context(request)

        # Get 12 most recent research items for the grid
        context['research_items'] = ResearchItem.objects.all().order_by(
            '-publish_date', '-created_at'
        )[:12]

        # Get current Global Peptide Group for homepage feature
        from home.models import GlobalPeptideGroupPage
        current_gpg = GlobalPeptideGroupPage.objects.live().public().filter(
            is_current=True
        ).first()
        context['current_gpg'] = current_gpg

        return context


# =============================================================================
# RESEARCH ITEM CATEGORY
# =============================================================================

@register_snippet
class ResearchItemCategory(models.Model):
    """
    Categories for research items (used on Archive page filtering only).

    6 Categories:
    1. Synthesis & Methods
    2. Structure & Design
    3. Delivery & Penetration
    4. Therapeutics & Discovery
    5. Natural Products & RiPPs
    6. Mechanisms & Probes
    """
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    panels = [
        FieldPanel('name'),
    ]

    class Meta:
        verbose_name = "Research Category"
        verbose_name_plural = "Research Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# =============================================================================
# RESEARCH ITEM
# =============================================================================

@register_snippet
class ResearchItem(models.Model):
    """
    Research/News article snippet.

    Workflow: Scopus → PhD review → Claude synthesis → PI approval → publish

    Display contexts:
    - Homepage F-layout cards: image, short_title, lab_name, publish_date
    - Archive page: + blurb, category filter
    - Detail page: full article with all fields
    """

    # =========================================================================
    # HOMEPAGE CARD DISPLAY
    # =========================================================================
    short_title = models.CharField(
        max_length=100,
        help_text="Display title for cards, e.g., 'Modeling Selectivity'"
    )
    lab_name = models.CharField(
        max_length=100,
        help_text="Lab name for cards, e.g., 'Miller Lab'"
    )
    main_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Main figure/graphic (recommended: 973x670px)"
    )
    main_image_caption = models.TextField(
        blank=True,
        help_text="Caption for main figure (HTML allowed)"
    )
    publish_date = models.DateField(
        default=timezone.now,
        help_text="Date displayed on cards and used for ordering"
    )

    # =========================================================================
    # ARCHIVE / SOCIAL
    # =========================================================================
    blurb = models.TextField(
        blank=True,
        help_text="Brief summary for archive listings and social sharing (not shown on homepage)"
    )
    category = models.ForeignKey(
        ResearchItemCategory,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='research_items',
        help_text="Category for archive page filtering"
    )

    # =========================================================================
    # ARTICLE CONTENT
    # =========================================================================
    body = models.TextField(
        help_text="Full synthesized article - paste raw HTML with inline styles"
    )

    # =========================================================================
    # PUBLICATION INFORMATION
    # =========================================================================
    publication_title = models.CharField(
        max_length=500,
        help_text="Full title of the original journal article"
    )
    publication_authors = models.TextField(
        help_text="Author list from the publication"
    )
    publication_citation = models.CharField(
        max_length=300,
        help_text="Citation: Journal, Year, Volume, Pages (HTML allowed for italics)"
    )
    publication_url = models.URLField(
        help_text="DOI or journal link"
    )

    # =========================================================================
    # PRINCIPAL INVESTIGATOR
    # =========================================================================
    pi_first_name = models.CharField(max_length=100)
    pi_last_name = models.CharField(max_length=100)
    pi_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="e.g., 'Professor', 'Associate Professor'"
    )
    pi_institution = models.CharField(
        max_length=300,
        help_text="Institution or company"
    )
    pi_url = models.URLField(
        blank=True,
        help_text="PI's lab or profile page"
    )

    # =========================================================================
    # FIRST AUTHOR SPOTLIGHT 1
    # =========================================================================
    author_1_info = models.TextField(
        blank=True,
        help_text="First author bio (HTML allowed)"
    )
    author_1_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="First author photo"
    )

    # =========================================================================
    # FIRST AUTHOR SPOTLIGHT 2
    # =========================================================================
    author_2_info = models.TextField(
        blank=True,
        help_text="Second author bio (HTML allowed)"
    )
    author_2_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Second author photo"
    )

    # =========================================================================
    # FIRST AUTHOR SPOTLIGHT 3
    # =========================================================================
    author_3_info = models.TextField(
        blank=True,
        help_text="Third author bio (HTML allowed)"
    )
    author_3_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Third author photo"
    )

    # =========================================================================
    # META
    # =========================================================================
    slug = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        help_text="Auto-generated from short title"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # =========================================================================
    # ADMIN PANELS
    # =========================================================================
    panels = [
        MultiFieldPanel([
            FieldPanel('short_title'),
            FieldPanel('lab_name'),
            FieldPanel('publish_date'),
            FieldPanel('category'),
        ], heading="Card Display & Metadata"),

        MultiFieldPanel([
            FieldPanel('main_image'),
            FieldPanel('main_image_caption'),
        ], heading="Main Figure"),

        MultiFieldPanel([
            FieldPanel('blurb'),
            FieldPanel('body'),
        ], heading="Article Content"),

        MultiFieldPanel([
            FieldPanel('publication_title'),
            FieldPanel('publication_authors'),
            FieldPanel('publication_citation'),
            FieldPanel('publication_url'),
        ], heading="Publication Information"),

        MultiFieldPanel([
            FieldPanel('pi_first_name'),
            FieldPanel('pi_last_name'),
            FieldPanel('pi_title'),
            FieldPanel('pi_institution'),
            FieldPanel('pi_url'),
        ], heading="Principal Investigator"),

        MultiFieldPanel([
            FieldPanel('author_1_image'),
            FieldPanel('author_1_info'),
        ], heading="First Author Spotlight 1"),

        MultiFieldPanel([
            FieldPanel('author_2_image'),
            FieldPanel('author_2_info'),
        ], heading="First Author Spotlight 2"),

        MultiFieldPanel([
            FieldPanel('author_3_image'),
            FieldPanel('author_3_info'),
        ], heading="First Author Spotlight 3"),
    ]

    class Meta:
        verbose_name = "Research Item"
        verbose_name_plural = "Research Items"
        ordering = ['-publish_date', '-created_at']

    def __str__(self):
        return self.short_title

    def save(self, *args, **kwargs):
        # Auto-generate slug from short_title
        if not self.slug:
            base_slug = slugify(self.short_title)
            slug = base_slug
            counter = 2
            while ResearchItem.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('research_item_detail', kwargs={'slug': self.slug})

    @property
    def pi_full_name(self):
        return f"{self.pi_first_name} {self.pi_last_name}"


# =============================================================================
# SYMPOSIUM IMAGE
# =============================================================================

@register_snippet
class SymposiumImage(models.Model):
    """
    Images from APS Symposium events, organized by year.
    Uses Wagtail image system for automatic renditions.
    """
    YEAR_CHOICES = [
        (2015, '2015 - Orlando'),
        (2017, '2017 - Whistler'),
        (2019, '2019 - Monterey'),
        (2022, '2022 - Whistler'),
        (2023, '2023 - Tucson'),
        (2025, '2025 - San Diego'),
    ]

    year = models.IntegerField(choices=YEAR_CHOICES)
    image = models.ForeignKey(
        'wagtailimages.Image',
        on_delete=models.CASCADE,
        related_name='+'
    )
    caption = models.CharField(max_length=500, blank=True)
    photographer = models.CharField(max_length=200, blank=True)
    sort_order = models.IntegerField(default=0)

    panels = [
        FieldPanel('year'),
        FieldPanel('image'),
        FieldPanel('caption'),
        FieldPanel('photographer'),
        FieldPanel('sort_order'),
    ]

    class Meta:
        verbose_name = "Symposium Image"
        verbose_name_plural = "Symposium Images"
        ordering = ['-year', 'sort_order']

    def __str__(self):
        return f"{self.year} - {self.caption[:50] if self.caption else self.image.title}"


# =============================================================================
# SYMPOSIUM GALLERY PAGE
# =============================================================================

# =============================================================================
# RESEARCH AREA (for PeptideLinks)
# =============================================================================

@register_snippet
class ResearchArea(models.Model):
    """Research areas/specializations for researchers"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    slug = models.SlugField(unique=True, blank=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]

    class Meta:
        verbose_name = "Research Area"
        verbose_name_plural = "Research Areas"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


# =============================================================================
# RESEARCHER (for PeptideLinks)
# =============================================================================

@register_snippet
class Researcher(models.Model):
    """
    Peptide researcher for the PeptideLinks directory.
    Migrated from peptidelinks.net - 426 researchers with ORCID, PubMed integration.
    """

    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    title = models.CharField(max_length=200, blank=True, help_text="e.g., Professor, Associate Professor")

    # Institution Details
    institution = models.CharField(max_length=200)
    department = models.CharField(max_length=200, blank=True)

    # Geographic Information
    country = models.CharField(max_length=100, default="USA")
    state_province = models.CharField(max_length=100, blank=True, help_text="State (US) or Province (Canada)")
    city = models.CharField(max_length=100, blank=True)

    # Contact & Web Presence
    website_url = models.URLField(blank=True, help_text="Personal or lab website")
    orcid_id = models.CharField(max_length=50, blank=True, help_text="ORCID identifier (e.g., 0000-0000-0000-0000)")

    # PubMed Integration
    pubmed_url = models.URLField(blank=True)

    # Google Scholar Integration
    google_scholar_url = models.URLField(blank=True, help_text="Google Scholar profile URL")

    # Research Areas
    research_areas = models.ManyToManyField(ResearchArea, blank=True, related_name='researchers')
    research_keywords = models.TextField(blank=True, help_text="Comma-separated keywords")

    # Administrative Fields
    is_active = models.BooleanField(default=True, help_text="Display in public directory")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        MultiFieldPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
            FieldPanel('title'),
        ], heading="Personal Information"),

        MultiFieldPanel([
            FieldPanel('institution'),
            FieldPanel('department'),
            FieldPanel('country'),
            FieldPanel('state_province'),
            FieldPanel('city'),
        ], heading="Institution & Location"),

        MultiFieldPanel([
            FieldPanel('website_url'),
            FieldPanel('orcid_id'),
            FieldPanel('pubmed_url'),
            FieldPanel('google_scholar_url'),
        ], heading="Web Presence"),

        MultiFieldPanel([
            FieldPanel('research_areas'),
            FieldPanel('research_keywords'),
        ], heading="Research"),

        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = "Researcher"
        verbose_name_plural = "Researchers"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.last_name}, {self.first_name} - {self.institution}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def orcid_url(self):
        if self.orcid_id:
            return f"https://orcid.org/{self.orcid_id}"
        return ""


# =============================================================================
# PEPTIDE LINKS INDEX PAGE
# =============================================================================

class PeptideLinksIndexPage(Page):
    """
    Directory page for peptide researchers (PeptideLinks).
    Supports filtering by country, state, research area, and search.
    """
    intro = models.TextField(
        blank=True,
        help_text="Introduction text for the page"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Split intro into two paragraphs for two-column layout
        if self.intro:
            paragraphs = self.intro.strip().split('\n\n')
            context['intro_paragraph_1'] = paragraphs[0] if len(paragraphs) > 0 else ''
            # Combine remaining paragraphs for second column
            context['intro_paragraph_2'] = '\n\n'.join(paragraphs[1:]) if len(paragraphs) > 1 else ''

        # Start with all active researchers
        researchers = Researcher.objects.filter(is_active=True)

        # Get filter parameters
        country = request.GET.get('country', '')
        state = request.GET.get('state', '')
        area = request.GET.get('area', '')
        search = request.GET.get('q', '')
        letter = request.GET.get('letter', '')

        # Apply filters
        if country:
            researchers = researchers.filter(country=country)
        if state:
            researchers = researchers.filter(state_province=state)
        if area:
            researchers = researchers.filter(research_areas__slug=area)
        if letter:
            researchers = researchers.filter(last_name__istartswith=letter)
        if search:
            from django.db.models import Q
            researchers = researchers.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(institution__icontains=search) |
                Q(research_keywords__icontains=search)
            )

        # Remove duplicates from many-to-many filtering
        researchers = researchers.distinct()

        # Get filter options (from all active researchers)
        all_researchers = Researcher.objects.filter(is_active=True)
        context['countries'] = all_researchers.values_list('country', flat=True).distinct().order_by('country')
        context['states'] = all_researchers.exclude(state_province='').values_list('state_province', flat=True).distinct().order_by('state_province')
        context['research_areas'] = ResearchArea.objects.all()

        # Alphabet for letter filter
        context['alphabet'] = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')

        # Current filters for template
        context['current_country'] = country
        context['current_state'] = state
        context['current_area'] = area
        context['current_search'] = search
        context['current_letter'] = letter

        # Results
        context['researchers'] = researchers
        context['total_count'] = researchers.count()

        return context


class SymposiumGalleryPage(Page):
    """
    Gallery page displaying symposium images organized by year.
    """
    intro = models.TextField(
        blank=True,
        help_text="Introduction text for the gallery page"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    # Complete symposium data: location, banner, title, description
    SYMPOSIUM_DATA = {
        2015: {
            'location': 'Orlando',
            'banner': 'symposium_banners/2015_orlando.jpg',
            'title': 'Images from APS Symposium 2015',
            'description': '''The theme for the 24th American Peptide Symposium was "Enabling Peptide Research from Basic Science to Drug Discovery" and was held at the Hyatt Regency Grand Cypress, Orlando, FL. Chairs were Ved Srivastava, then with GlaxoSmithKline, and Andrei Yudin, University of Toronto.

The scientific program for 2015 opened with a lecture by Dr. Richard A. Lerner of The Scripps Research Institute and was concluded with a lecture by Dr. Jeffrey Friedman of the Rockefeller Institute. We hope you find friends, colleagues, memories, and perhaps yourself among the images from below.'''
        },
        2017: {
            'location': 'Whistler',
            'banner': 'symposium_banners/2017_whistler.jpg',
            'title': 'Images from APS Symposium 2017',
            'description': '''The theme for the 25th American Peptide Symposium was "New Heights in Peptide Research" and was held at the Whistler Conference Centre, Whistler, BC, Canada. Chairs were Jonathan Lai, Albert Einstein College of Medicine, and John Vederas, University of Alberta.

The scientific program for 2017 opened with a lecture by Dr. Richard A. Lerner of The Scripps Research Institute and was concluded by Dr. Jeffrey Friedman of the Rockefeller Institute. We hope you find friends, colleagues, memories, and perhaps yourself among the images from below.'''
        },
        2019: {
            'location': 'Monterey',
            'banner': 'symposium_banners/2019_monterey.jpg',
            'title': 'Images from APS Symposium 2019',
            'description': '''The theme for the 26th American Peptide Symposium was "Catch the Wave of Peptide Science" and it was held at the Portola Hotel & Monterey Conference Center, Monterey, CA. Chairs were Paramjit Arora, New York University, and Anna Mapp, University of Michigan.

Nobel Laureate Frances Arnold of the California Institute of Technology opened the symposium with her lecture "Innovation by Evolution: Bringing New Chemistry to Life." The closing lecture was held by Professor Helma Wennemers of ETH-Zurich on "Controlling Supramolecular Assemblies with Peptidic Scaffolds."'''
        },
        2022: {
            'location': 'Whistler',
            'banner': 'symposium_banners/2022_whistler.jpg',
            'title': 'Images from APS Symposium 2022',
            'description': '''The theme for the 27th American Peptide Symposium, "Peptide Science at the Summit", held at The Whistler Conference Centre, Whistler, BC, Canada, covered a broad range of topics connecting chemical, structural, materials, biological, pharmaceutical and medical science. Co-Chairs were Mark D. Distefano from the University of Minnesota, and Les Miranda from Amgen.

Melissa Moore, Chief Scientific Officer of Moderna, opened the symposium with her keynote lecture titled "mRNA as Medicine". The closing keynote lecture, "Discovery and Applications of Cyclotides: Nature's Ultra-Stable Peptide Scaffolds," was performed by Professor David Craik from the University of Queensland.'''
        },
        2023: {
            'location': 'Tucson',
            'banner': 'symposium_banners/2023_tucson.jpg',
            'title': 'Images from APS Symposium 2023',
            'description': '''The theme for the 28th American Peptide Symposium, "At the Peptide Frontier", conveyed that this Symposium would feature emerging peptide research at the forefront of chemical, structural, materials, biological, pharmaceutical and medical science. Co-Chairs were David Chenowith from the University of Pennsylvania, and Robert Garbaccio, Head of Discovery Chemistry at Merck.

Professor Laura L. Kiessling from Massachusetts Institute of Technology opened the symposium with her keynote lecture "Peptide-Glycan Interactions in Immunity." The closing keynote lecture, "Pirating Biology to Probe and Modulate the Cell Surfaceome," was performed by Professor Jim Wells, University of California at San Francisco.'''
        },
        2025: {
            'location': 'San Diego',
            'banner': 'symposium_banners/2025_san_diego.jpg',
            'title': 'Images from APS Symposium 2025',
            'description': '''The 29th American Peptide Symposium represented a showcase of scientific excellence, groundbreaking research, and global collaboration. With record-breaking attendance, the energy in San Diego was electric — a reflection of the surging impact of peptide science across disciplines. Attendees were treated to an extraordinary lineup of talks, spanning from the frontiers of peptide therapeutics to innovations in sustainable manufacturing, AI-driven drug discovery, structural biology, material science, and computational design. The theme of "Peptides Rising" truly encapsulated the momentum of the field — with sessions designed to highlight the most pressing challenges and the most exciting breakthroughs.

Our keynote lectures by Dame Margaret Brimble and Dr. Scott Miller were nothing short of inspiring, while award lectures from luminaries like Dek Woolfson, Ashraf Brik, Phil Dawson, Krishna Kumar, William Lubell, and Elizabeth Parkinson brought depth, vision, and creativity to center stage. This year's Symposium wasn't just a meeting, it was a celebration of the resilience, creativity, and boundless curiosity that defines the global peptide community. The future of peptide science has never looked brighter, and is indeed rising.'''
        },
    }

    def get_context(self, request):
        context = super().get_context(request)

        # Get all years that have images
        years = list(SymposiumImage.objects.values_list('year', flat=True).distinct().order_by('-year'))

        # Build year data with locations
        context['year_data'] = [
            {'year': y, 'location': self.SYMPOSIUM_DATA.get(y, {}).get('location', '')}
            for y in years
        ]

        # Get the active year (from query param or most recent)
        active_year = request.GET.get('year')
        if active_year:
            try:
                active_year = int(active_year)
            except ValueError:
                active_year = None

        if not active_year and years:
            active_year = years[0]

        context['active_year'] = active_year

        # Get symposium data for active year
        if active_year and active_year in self.SYMPOSIUM_DATA:
            symposium = self.SYMPOSIUM_DATA[active_year]
            context['symposium_title'] = symposium['title']
            context['symposium_banner'] = symposium['banner']
            context['symposium_location'] = symposium['location']

            # Split description into two paragraphs for two-column layout
            paragraphs = symposium['description'].strip().split('\n\n')
            context['symposium_paragraph_1'] = paragraphs[0] if len(paragraphs) > 0 else ''
            context['symposium_paragraph_2'] = paragraphs[1] if len(paragraphs) > 1 else ''

        # Get images for active year
        if active_year:
            context['images'] = SymposiumImage.objects.filter(year=active_year).order_by('sort_order')
        else:
            context['images'] = SymposiumImage.objects.none()

        return context


# =============================================================================
# APS PEOPLE - Officers, Councilors, Past Presidents, Committees
# =============================================================================

@register_snippet
class APSRole(models.Model):
    """
    Roles within APS (President, Secretary, Councilor, etc.)
    Used for flexible role assignment with service dates.
    """
    CATEGORY_CHOICES = [
        ('officer', 'Officer'),
        ('councilor', 'Councilor'),
        ('staff', 'Staff'),
        ('past_president', 'Past President'),
    ]

    name = models.CharField(max_length=100, unique=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    display_order = models.IntegerField(
        default=0,
        help_text="Order for display (lower numbers first)"
    )

    panels = [
        FieldPanel('name'),
        FieldPanel('category'),
        FieldPanel('display_order'),
    ]

    class Meta:
        verbose_name = "APS Role"
        verbose_name_plural = "APS Roles"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


@register_snippet
class APSCommittee(models.Model):
    """APS Committees (Awards, Symposium, etc.)"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    display_order = models.IntegerField(default=0)

    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('display_order'),
    ]

    class Meta:
        verbose_name = "APS Committee"
        verbose_name_plural = "APS Committees"
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


@register_snippet
class APSPerson(ClusterableModel):
    """
    APS People - Officers, Councilors, Committee Members, Past Presidents.
    Uses inline panels for role assignments and committee memberships.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    professional_title = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g., Professor, Associate Professor, Ph.D."
    )
    institution = models.CharField(max_length=255, blank=True)

    # Photo
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # Contact (optional)
    email = models.EmailField(blank=True)
    website_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide from public pages"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
            FieldPanel('professional_title'),
            FieldPanel('institution'),
        ], heading="Personal Information"),

        FieldPanel('photo'),

        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('website_url'),
        ], heading="Contact (Optional)"),

        InlinePanel('role_assignments', label="Role Assignments"),
        InlinePanel('committee_memberships', label="Committee Memberships"),

        FieldPanel('is_active'),
    ]

    class Meta:
        verbose_name = "APS Person"
        verbose_name_plural = "APS People"
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def current_roles(self):
        """Get all current role assignments"""
        return self.role_assignments.filter(is_current=True)

    @property
    def current_role_display(self):
        """Get the primary current role for display"""
        current = self.role_assignments.filter(is_current=True).first()
        return current.role.name if current else ""


class PersonRoleAssignment(models.Model):
    """
    Links a person to a role with service dates.
    Allows tracking historical roles and current assignments.
    """
    person = ParentalKey(
        APSPerson,
        on_delete=models.CASCADE,
        related_name='role_assignments'
    )
    role = models.ForeignKey(
        APSRole,
        on_delete=models.CASCADE,
        related_name='assignments'
    )
    service_start = models.DateField(
        null=True,
        blank=True,
        help_text="When this role began"
    )
    service_end = models.DateField(
        null=True,
        blank=True,
        help_text="When this role ended (leave blank if current)"
    )
    is_current = models.BooleanField(
        default=True,
        help_text="Currently holds this role"
    )

    panels = [
        FieldPanel('role'),
        FieldPanel('service_start'),
        FieldPanel('service_end'),
        FieldPanel('is_current'),
    ]

    class Meta:
        verbose_name = "Role Assignment"
        verbose_name_plural = "Role Assignments"
        ordering = ['-is_current', '-service_start']

    def __str__(self):
        return f"{self.person} - {self.role}"

    @property
    def service_years(self):
        """Display service years like '2023 - 2025' or '2023 - Present'"""
        if self.service_start:
            start = self.service_start.year
            if self.service_end:
                return f"{start} – {self.service_end.year}"
            elif self.is_current:
                return f"{start} – Present"
            return str(start)
        return ""


class PersonCommitteeMembership(models.Model):
    """Links a person to a committee with role (chair/member)"""
    MEMBERSHIP_ROLE_CHOICES = [
        ('chair', 'Chair'),
        ('co_chair', 'Co-Chair'),
        ('member', 'Member'),
    ]

    person = ParentalKey(
        APSPerson,
        on_delete=models.CASCADE,
        related_name='committee_memberships'
    )
    committee = models.ForeignKey(
        APSCommittee,
        on_delete=models.CASCADE,
        related_name='memberships'
    )
    membership_role = models.CharField(
        max_length=20,
        choices=MEMBERSHIP_ROLE_CHOICES,
        default='member'
    )
    is_current = models.BooleanField(default=True)

    panels = [
        FieldPanel('committee'),
        FieldPanel('membership_role'),
        FieldPanel('is_current'),
    ]

    class Meta:
        verbose_name = "Committee Membership"
        verbose_name_plural = "Committee Memberships"
        ordering = ['committee__display_order', '-membership_role']

    def __str__(self):
        return f"{self.person} - {self.membership_role} of {self.committee}"


# =============================================================================
# PEOPLE INDEX PAGE - 2+10 Sidebar Layout
# =============================================================================

class PeopleIndexPage(Page):
    """
    People directory page with sidebar navigation.
    Shows Officers & Councilors, Past Presidents, or Committees based on view.
    """
    intro = models.TextField(
        blank=True,
        help_text="Introduction text (two paragraphs separated by blank line)"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    # View configurations
    VIEWS = {
        'officers': {
            'title': 'Officers & Councilors',
            'description': '''The American Peptide Society is governed by elected Officers and Councilors who volunteer their time and expertise to advance the mission of the society. Officers serve two-year terms and are responsible for the strategic direction and day-to-day operations of the organization.

Councilors serve six-year terms and provide guidance on society initiatives, symposium planning, awards, and membership development. Together, this leadership team works to promote peptide science education, foster collaboration, and support the peptide research community worldwide.'''
        },
        'past-presidents': {
            'title': 'Past Presidents',
            'description': '''The American Peptide Society has been fortunate to have exceptional leaders guide the organization since its founding. Our past presidents have shaped the society's mission, expanded its reach, and advanced the field of peptide science through their vision and dedication.

We honor their contributions and the lasting impact they have made on our community. Their leadership has helped establish the APS as the premier organization for peptide scientists worldwide.'''
        },
        'committees': {
            'title': 'APS Committees',
            'description': '''The work of the American Peptide Society is carried out through dedicated committees that oversee key aspects of our mission. Committee members volunteer their expertise to organize symposia, select award recipients, develop educational programs, and support student initiatives.

These committees are essential to the society's success, and we are grateful for the service of all committee members who contribute their time and knowledge to advance peptide science.'''
        },
    }

    def get_context(self, request):
        context = super().get_context(request)

        # Get current view (default to officers)
        view = request.GET.get('view', 'officers')
        if view not in self.VIEWS:
            view = 'officers'

        context['current_view'] = view
        context['view_config'] = self.VIEWS[view]

        # Navigation items for sidebar
        context['nav_items'] = [
            {'key': 'officers', 'label': 'Officers & Councilors', 'icon': 'people'},
            {'key': 'past-presidents', 'label': 'Past Presidents', 'icon': 'award'},
            {'key': 'committees', 'label': 'Committees', 'icon': 'diagram-3'},
        ]

        # Split description into two paragraphs
        desc = self.VIEWS[view]['description']
        paragraphs = desc.strip().split('\n\n')
        context['description_1'] = paragraphs[0] if len(paragraphs) > 0 else ''
        context['description_2'] = paragraphs[1] if len(paragraphs) > 1 else ''

        # Load data based on view
        if view == 'officers':
            # Get current officers and councilors
            officers = APSPerson.objects.filter(
                is_active=True,
                role_assignments__is_current=True,
                role_assignments__role__category='officer'
            ).distinct().prefetch_related('role_assignments__role')

            councilors = APSPerson.objects.filter(
                is_active=True,
                role_assignments__is_current=True,
                role_assignments__role__category='councilor'
            ).distinct().prefetch_related('role_assignments__role')

            staff = APSPerson.objects.filter(
                is_active=True,
                role_assignments__is_current=True,
                role_assignments__role__category='staff'
            ).distinct().prefetch_related('role_assignments__role')

            # Sort officers by role display order
            context['officers'] = sorted(
                officers,
                key=lambda p: p.role_assignments.filter(
                    is_current=True, role__category='officer'
                ).first().role.display_order if p.role_assignments.filter(
                    is_current=True, role__category='officer'
                ).first() else 999
            )
            context['councilors'] = councilors.order_by('last_name')
            context['staff'] = staff.order_by('last_name')

        elif view == 'past-presidents':
            # Get past presidents ordered by service end date (most recent first)
            past_presidents = APSPerson.objects.filter(
                is_active=True,
                role_assignments__role__category='past_president'
            ).distinct().prefetch_related('role_assignments__role')

            # Sort by most recent service end date
            context['past_presidents'] = sorted(
                past_presidents,
                key=lambda p: (
                    p.role_assignments.filter(role__category='past_president').first().service_end
                    or p.role_assignments.filter(role__category='past_president').first().service_start
                ) if p.role_assignments.filter(role__category='past_president').first() else None,
                reverse=True
            )

        elif view == 'committees':
            # Get all committees with current members
            committees = APSCommittee.objects.prefetch_related(
                'memberships__person'
            ).filter(
                memberships__is_current=True
            ).distinct().order_by('display_order', 'name')

            # Build committee data with sorted members (chairs first)
            committee_data = []
            for committee in committees:
                members = committee.memberships.filter(
                    is_current=True
                ).select_related('person').order_by(
                    '-membership_role',  # chair, co_chair, member
                    'person__last_name'
                )
                committee_data.append({
                    'committee': committee,
                    'members': members
                })

            context['committees'] = committee_data

        return context

    class Meta:
        verbose_name = "People Index Page"


# =============================================================================
# AWARDS - Merrifield, du Vigneaud, Goodman, Makineni, Early Career, Hirschmann
# =============================================================================

@register_snippet
class AwardType(models.Model):
    """
    Represents different types of awards given by the American Peptide Society.
    """
    slug = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    short_name = models.CharField(
        max_length=50,
        blank=True,
        help_text="Short name for navigation buttons"
    )
    description = models.TextField(blank=True)

    # Sponsor information
    sponsor_name = models.CharField(max_length=200, blank=True)
    sponsor_description = models.TextField(blank=True)
    sponsor_logo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    sponsor_url = models.URLField(blank=True)

    # Additional content (e.g., Merrifield essay link)
    additional_content = models.TextField(
        blank=True,
        help_text="Additional content like essay links (HTML allowed)"
    )

    # Display settings
    display_order = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)

    panels = [
        FieldPanel('name'),
        FieldPanel('short_name'),
        FieldPanel('slug'),
        FieldPanel('description'),
        MultiFieldPanel([
            FieldPanel('sponsor_name'),
            FieldPanel('sponsor_description'),
            FieldPanel('sponsor_logo'),
            FieldPanel('sponsor_url'),
        ], heading="Sponsor Information"),
        FieldPanel('additional_content'),
        FieldPanel('display_order'),
        FieldPanel('is_active'),
    ]

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Award Type"
        verbose_name_plural = "Award Types"

    def __str__(self):
        return self.name


@register_snippet
class AwardRecipient(models.Model):
    """Individual recipient of an APS award."""
    award_type = models.ForeignKey(
        AwardType,
        on_delete=models.CASCADE,
        related_name='recipients'
    )
    year = models.IntegerField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    institution = models.CharField(max_length=255, blank=True)
    biography = models.TextField(blank=True)
    slug = models.SlugField(
        max_length=150,
        unique=True,
        blank=True,
        help_text="Auto-generated from name and year"
    )

    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    panels = [
        FieldPanel('award_type'),
        FieldPanel('year'),
        FieldPanel('first_name'),
        FieldPanel('last_name'),
        FieldPanel('institution'),
        FieldPanel('biography'),
        FieldPanel('photo'),
    ]

    class Meta:
        ordering = ['-year', 'last_name']
        verbose_name = "Award Recipient"
        verbose_name_plural = "Award Recipients"
        unique_together = ['award_type', 'year', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.year})"

    def save(self, *args, **kwargs):
        # Auto-generate slug from name and year
        if not self.slug:
            base_slug = slugify(f"{self.first_name}-{self.last_name}-{self.year}")
            slug = base_slug
            counter = 2
            while AwardRecipient.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('award_recipient_detail', kwargs={'slug': self.slug})

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"


# =============================================================================
# AWARDS INDEX PAGE - 2+6+4 Sidebar Layout
# =============================================================================

class AwardsIndexPage(Page):
    """
    Awards directory page with sidebar navigation.
    Layout: 2-col nav | 6-col awardees | 4-col sponsor
    """
    intro = models.TextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request):
        context = super().get_context(request)

        # Get all active award types for navigation
        award_types = AwardType.objects.filter(is_active=True)
        context['award_types'] = award_types

        # Get current award (from query param or default to first)
        award_slug = request.GET.get('award')
        if award_slug:
            current_award = award_types.filter(slug=award_slug).first()
        else:
            current_award = award_types.first()

        context['current_award'] = current_award

        if current_award:
            # Get recipients grouped by decade
            recipients = current_award.recipients.all().order_by('-year')

            # Group by decade
            recipients_by_decade = {}
            for recipient in recipients:
                decade = (recipient.year // 10) * 10
                decade_key = f"{decade}s"
                if decade_key not in recipients_by_decade:
                    recipients_by_decade[decade_key] = []
                recipients_by_decade[decade_key].append(recipient)

            # Sort decades descending
            sorted_decades = sorted(
                recipients_by_decade.items(),
                key=lambda x: x[0],
                reverse=True
            )

            context['recipients_by_decade'] = sorted_decades
            context['total_recipients'] = recipients.count()

        return context

    class Meta:
        verbose_name = "Awards Index Page"


# =============================================================================
# GLOBAL PEPTIDE GROUPS (formerly Lab of the Month)
# =============================================================================

class TabBlock(StructBlock):
    """
    A single tab with title and raw HTML content.
    Content accepts full HTML including Bootstrap columns, images, etc.
    """
    title = CharBlock(
        max_length=100,
        help_text="Tab title (e.g., 'WHO WE ARE', 'OUR RESEARCH')"
    )
    content = TextBlock(
        help_text="Raw HTML content for this tab. Supports Bootstrap columns, images, etc."
    )

    class Meta:
        icon = 'doc-full'
        label = 'Tab'


class GlobalPeptideGroupPage(Page):
    """
    A single Global Peptide Group feature page with tabbed content.
    Each page showcases a research lab with multiple tabs of content.
    """
    lab_name = models.CharField(
        max_length=200,
        help_text="Full lab name (e.g., 'The Craik Group')"
    )
    pi_name = models.CharField(
        max_length=200,
        blank=True,
        help_text="Principal Investigator name"
    )
    institution = models.CharField(
        max_length=300,
        blank=True,
        help_text="Institution name"
    )
    featured_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Image shown on archive page and as banner"
    )
    blurb = models.TextField(
        blank=True,
        help_text="Short description for homepage/archive display"
    )
    feature_date = models.DateField(
        null=True,
        blank=True,
        help_text="Month/year when this group was featured"
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Mark as currently featured group"
    )
    tabs = StreamField(
        [('tab', TabBlock())],
        blank=True,
        use_json_field=True,
        help_text="Add tabs with content for this group's page"
    )
    old_url_slug = models.CharField(
        max_length=200,
        blank=True,
        help_text="Original WordPress URL slug for redirect setup"
    )

    content_panels = Page.content_panels + [
        MultiFieldPanel([
            FieldPanel('lab_name'),
            FieldPanel('pi_name'),
            FieldPanel('institution'),
        ], heading="Lab Information"),
        FieldPanel('featured_image'),
        FieldPanel('blurb'),
        MultiFieldPanel([
            FieldPanel('feature_date'),
            FieldPanel('is_current'),
        ], heading="Feature Status"),
        FieldPanel('tabs'),
        FieldPanel('old_url_slug'),
    ]

    parent_page_types = ['home.GlobalPeptideGroupIndexPage']
    subpage_types = []

    class Meta:
        verbose_name = "Global Peptide Group Page"
        verbose_name_plural = "Global Peptide Group Pages"


class GlobalPeptideGroupIndexPage(Page):
    """
    Index page listing all Global Peptide Group features.
    Shows archive grid with filtering options.
    """
    intro = models.TextField(
        blank=True,
        help_text="Introduction text for the archive page"
    )

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    subpage_types = ['home.GlobalPeptideGroupPage']

    def get_context(self, request):
        context = super().get_context(request)

        # Get all published group pages, newest first
        groups = GlobalPeptideGroupPage.objects.live().public().order_by('-feature_date', '-first_published_at')

        # Get the current featured group if any
        current_group = groups.filter(is_current=True).first()
        context['current_group'] = current_group

        # Archive excludes current if desired, or show all
        context['groups'] = groups

        return context

    class Meta:
        verbose_name = "Global Peptide Groups Index Page"


# =============================================================================
# IN MEMORIAM / OBITUARIES
# =============================================================================

@register_snippet
class InMemoriam(models.Model):
    """
    Represents a person who has passed away, honored in the In Memoriam section.
    """
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )

    # Short summary for index page
    blurb = models.TextField(
        blank=True,
        help_text="Short summary for the index page (HTML allowed)"
    )

    # Full obituary text for detail page
    full_text = models.TextField(
        blank=True,
        help_text="Full obituary content (HTML allowed)"
    )

    # Ordering - higher numbers appear first
    display_order = models.IntegerField(
        default=0,
        help_text="Higher numbers appear first"
    )

    panels = [
        FieldPanel('first_name'),
        FieldPanel('last_name'),
        FieldPanel('slug'),
        FieldPanel('photo'),
        FieldPanel('blurb'),
        FieldPanel('full_text'),
        FieldPanel('display_order'),
    ]

    class Meta:
        ordering = ['-display_order']
        verbose_name = "In Memoriam Entry"
        verbose_name_plural = "In Memoriam Entries"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(f"{self.first_name}-{self.last_name}")
            self.slug = base_slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('in_memoriam_detail', kwargs={'slug': self.slug})
