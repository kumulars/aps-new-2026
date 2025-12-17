# Peptide Postdocs Feature Specification

## Overview

This feature showcases postdoctoral researchers advancing peptide science. It appears on the APS homepage as a highlight panel with ~80-word blurbs, linking to full detail pages with tabbed content.

Homepage header: **Peptide Postdocs** — *Recognizing postdoctoral researchers advancing peptide science.*

---

## Wagtail Implementation

### Model: `PostdocProfile` (Snippet)

Location: `snippets/models.py` or dedicated `postdocs/models.py`

```python
from django.db import models
from wagtail.models import Page
from wagtail.fields import RichTextField
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.images.models import Image
from wagtail.snippets.models import register_snippet


@register_snippet
class PostdocProfile(models.Model):
    # === Core Identification ===
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=200)
    position_title = models.CharField(
        max_length=200,
        help_text="e.g., Feodor Lynen Research Fellow"
    )
    lab_name = models.CharField(max_length=200, help_text="e.g., Suga Lab")
    principal_investigator = models.CharField(max_length=200, blank=True)
    institution = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    
    # === External Links ===
    personal_website = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    
    # === Images ===
    headshot = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    headshot_credit = models.CharField(max_length=200, blank=True)
    lab_photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    lab_photo_caption = models.CharField(max_length=300, blank=True)
    
    # === Homepage Display ===
    homepage_blurb = models.TextField(
        max_length=600,
        help_text="~80 words / 500 characters for homepage display"
    )
    featured_on_homepage = models.BooleanField(default=False)
    publish_date = models.DateField()
    
    # === Tab: About / Research ===
    research_focus_short = models.TextField(
        max_length=500,
        help_text="1-2 sentence overview"
    )
    research_focus_full = RichTextField(
        help_text="Main narrative, APS-MATRIX style"
    )
    key_methods = models.CharField(
        max_length=500,
        blank=True,
        help_text="Comma-separated: mRNA display, RaPID, flexizymes, etc."
    )
    
    # === Tab: Path ===
    phd_institution = models.CharField(max_length=200)
    phd_supervisor = models.CharField(max_length=200)
    phd_year = models.CharField(max_length=10)
    thesis_title = models.CharField(max_length=500, blank=True)
    thesis_summary = models.TextField(blank=True)
    path_to_postdoc = RichTextField(
        blank=True,
        help_text="What drew them to current position"
    )
    international_perspective = RichTextField(
        blank=True,
        help_text="How moving between institutions shaped their thinking"
    )
    
    # === Tab: Publications ===
    publications = RichTextField(
        blank=True,
        help_text="Up to 3 selected publications with personal context"
    )
    
    # === Tab: Recognition ===
    awards_fellowships = RichTextField(
        blank=True,
        help_text="Awards, fellowships, conference highlights"
    )
    
    # === Tab: Reflections ===
    why_peptide_science = RichTextField(
        blank=True,
        help_text="What drew them in, what keeps them excited"
    )
    mentor_acknowledgments = RichTextField(blank=True)
    advice_to_students = models.TextField(blank=True)
    
    # === Tab: Beyond the Bench ===
    personal_interests = models.TextField(
        blank=True,
        help_text="Hobbies, life outside lab"
    )
    personal_story = models.TextField(
        blank=True,
        help_text="A small detail that captures who they are"
    )

    panels = [
        MultiFieldPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
            FieldPanel('slug'),
            FieldPanel('position_title'),
            FieldPanel('lab_name'),
            FieldPanel('principal_investigator'),
            FieldPanel('institution'),
            FieldPanel('country'),
        ], heading="Core Identification"),
        
        MultiFieldPanel([
            FieldPanel('personal_website'),
            FieldPanel('linkedin_url'),
            FieldPanel('twitter_url'),
            FieldPanel('google_scholar_url'),
        ], heading="External Links"),
        
        MultiFieldPanel([
            FieldPanel('headshot'),
            FieldPanel('headshot_credit'),
            FieldPanel('lab_photo'),
            FieldPanel('lab_photo_caption'),
        ], heading="Images"),
        
        MultiFieldPanel([
            FieldPanel('homepage_blurb'),
            FieldPanel('featured_on_homepage'),
            FieldPanel('publish_date'),
        ], heading="Homepage Display"),
        
        MultiFieldPanel([
            FieldPanel('research_focus_short'),
            FieldPanel('research_focus_full'),
            FieldPanel('key_methods'),
        ], heading="Research"),
        
        MultiFieldPanel([
            FieldPanel('phd_institution'),
            FieldPanel('phd_supervisor'),
            FieldPanel('phd_year'),
            FieldPanel('thesis_title'),
            FieldPanel('thesis_summary'),
            FieldPanel('path_to_postdoc'),
            FieldPanel('international_perspective'),
        ], heading="Career Path"),
        
        FieldPanel('publications'),
        FieldPanel('awards_fellowships'),
        
        MultiFieldPanel([
            FieldPanel('why_peptide_science'),
            FieldPanel('mentor_acknowledgments'),
            FieldPanel('advice_to_students'),
        ], heading="Reflections"),
        
        MultiFieldPanel([
            FieldPanel('personal_interests'),
            FieldPanel('personal_story'),
        ], heading="Beyond the Bench"),
    ]

    class Meta:
        ordering = ['-publish_date']
        verbose_name = "Postdoc Profile"
        verbose_name_plural = "Postdoc Profiles"

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
```

---

## Detail Page Template Structure

File: `templates/postdocs/postdoc_detail.html`

Use tabbed container matching "Global Peptide Groups" pattern:

```html
{% load wagtailimages_tags %}

<div class="postdoc-profile">
    <div class="postdoc-header">
        {% image postdoc.headshot fill-300x300 as headshot_img %}
        <img src="{{ headshot_img.url }}" alt="{{ postdoc.full_name }}">
        {% if postdoc.headshot_credit %}
            <p class="photo-credit">Photo: {{ postdoc.headshot_credit }}</p>
        {% endif %}
        
        <h1>{{ postdoc.full_name }}</h1>
        <p class="position">{{ postdoc.position_title }}</p>
        <p class="affiliation">{{ postdoc.lab_name }}, {{ postdoc.institution }}</p>
    </div>
    
    <div class="postdoc-tabs">
        <ul class="tab-nav">
            <li class="active"><a href="#about">About</a></li>
            <li><a href="#path">Path</a></li>
            <li><a href="#publications">Publications</a></li>
            <li><a href="#recognition">Recognition</a></li>
            <li><a href="#reflections">Reflections</a></li>
            <li><a href="#beyond">Beyond the Bench</a></li>
        </ul>
        
        <div id="about" class="tab-content active">
            <h3>Research Focus</h3>
            {{ postdoc.research_focus_full|safe }}
            {% if postdoc.key_methods %}
                <p><strong>Key Methods:</strong> {{ postdoc.key_methods }}</p>
            {% endif %}
        </div>
        
        <div id="path" class="tab-content">
            <h3>Doctoral Training</h3>
            <p><strong>{{ postdoc.phd_institution }}</strong> ({{ postdoc.phd_year }})<br>
            Supervisor: {{ postdoc.phd_supervisor }}</p>
            {% if postdoc.thesis_title %}
                <p><em>{{ postdoc.thesis_title }}</em></p>
            {% endif %}
            {{ postdoc.thesis_summary }}
            
            <h3>Path to Current Position</h3>
            {{ postdoc.path_to_postdoc|safe }}
            
            {% if postdoc.international_perspective %}
                <h3>International Perspective</h3>
                {{ postdoc.international_perspective|safe }}
            {% endif %}
        </div>
        
        <div id="publications" class="tab-content">
            <h3>Selected Publications</h3>
            {{ postdoc.publications|safe }}
        </div>
        
        <div id="recognition" class="tab-content">
            <h3>Awards &amp; Recognition</h3>
            {{ postdoc.awards_fellowships|safe }}
        </div>
        
        <div id="reflections" class="tab-content">
            <h3>Why Peptide Science?</h3>
            {{ postdoc.why_peptide_science|safe }}
            
            <h3>Mentors &amp; Influences</h3>
            {{ postdoc.mentor_acknowledgments|safe }}
            
            <h3>Advice to Students</h3>
            <blockquote>{{ postdoc.advice_to_students }}</blockquote>
        </div>
        
        <div id="beyond" class="tab-content">
            <h3>Outside the Lab</h3>
            <p>{{ postdoc.personal_interests }}</p>
            {% if postdoc.personal_story %}
                <p>{{ postdoc.personal_story }}</p>
            {% endif %}
        </div>
    </div>
    
    <div class="postdoc-links">
        {% if postdoc.personal_website %}<a href="{{ postdoc.personal_website }}">Website</a>{% endif %}
        {% if postdoc.linkedin_url %}<a href="{{ postdoc.linkedin_url }}">LinkedIn</a>{% endif %}
        {% if postdoc.twitter_url %}<a href="{{ postdoc.twitter_url }}">X/Twitter</a>{% endif %}
        {% if postdoc.google_scholar_url %}<a href="{{ postdoc.google_scholar_url }}">Google Scholar</a>{% endif %}
    </div>
</div>
```

---

## First Entry: Sven Ullrich

### Core Identification
```yaml
first_name: Sven
last_name: Ullrich
slug: sven-ullrich
position_title: Feodor Lynen Research Fellow (Humboldt Foundation)
lab_name: Suga Lab
principal_investigator: Professor Hiroaki Suga
institution: University of Tokyo
country: Japan
```

### External Links
```yaml
personal_website: https://www.svenullrich.com
linkedin_url: https://www.linkedin.com/in/sven-ullrich
twitter_url: https://www.x.com/s_ullr
google_scholar_url: https://scholar.google.com/citations?view_op=list_works&hl=en&user=Div3JI8AAAAJ
```

### Images
```yaml
headshot: [upload from attached files]
headshot_credit: Chenlian Wan (Instagram.com/wanchenlian)
lab_photo: [upload from attached files]
lab_photo_caption: [to be added based on image content]
```

### Homepage Display
```yaml
featured_on_homepage: true
publish_date: 2025-12-18
```

**homepage_blurb** (492 characters):
> Sven Ullrich explores mRNA display technology in the Suga Lab at the University of Tokyo, hunting for protease inhibitors against viral diseases. A Feodor Lynen Research Fellow, he earned dual Australian national awards for his Ph.D. on cyclic peptide therapeutics at ANU. His biocompatible bicyclic peptide work led to commercially available building blocks. Sven presented as a Young Investigator at APS 2024 San Diego and won the Schram Poster Award at Whistler 2022.

### Research

**research_focus_short**:
> Discovery of protease inhibitors for viral diseases through mRNA display; developing innovative peptide and protein cyclization methods toward constrained therapeutics.

**research_focus_full**:
```html
<p>Sven Ullrich investigates the discovery of new protease inhibitors for viral diseases through mRNA display while developing innovative peptide and protein cyclization methods. His work aims to find pathways toward powerful compact protein and constrained peptide therapeutics.</p>

<p>The mRNA display/RaPID platform stands at the center of his current research. Flexizymes, ribosomal translation, peptide libraries, and display technologies form his day-to-day toolkit. Many of these techniques were pioneered in the Suga Lab, and Sven values the opportunity to learn them directly "at the source."</p>
```

**key_methods**:
> mRNA display, RaPID platform, flexizymes, ribosomal translation, macrocyclic peptide libraries, display technologies

### Career Path

```yaml
phd_institution: Australian National University, Canberra, Australia
phd_supervisor: Associate Professor Christoph Nitsche
phd_year: "2024"
thesis_title: Modified Peptides as Viral Protease Inhibitors
```

**thesis_summary**:
> Development and evaluation of modified peptides, especially cyclic ones, against viral protease drug targets with a focus on Zika virus and SARS-CoV-2 proteases.

**path_to_postdoc**:
```html
<p>The first review paper Sven ever read when starting to work on cyclic peptides came from the Suga Lab: Vinogradov, Yin, and Suga's 2019 <em>JACS</em> review "Macrocyclic Peptides as Drug Candidates: Recent Progress and Remaining Challenges." He briefly overlapped with Dr. Alex Vinogradov, who now leads his own research group in Singapore.</p>

<p>Display technologies had always fascinated him. A research visit to Professor Derda's Lab at the University of Alberta introduced him to phage display, sparking his interest in comparing it with RaPID mRNA display. An Australia-wide research collaboration (CIPPS) on SARS-CoV-2 main protease, where Sven led the peptide evaluation, deepened his desire to learn the actual screening and selection process pioneered by Professor Suga.</p>
```

**international_perspective**:
```html
<p>We all are exposed to the same natural world, so the things we can discover are the same everywhere. What Sven has felt at every institution, and at conferences, is the shared passion for science—and that, he says, is a beautiful thing.</p>

<p>Since academic systems differ, environment shapes us more than we often realize. The best results come when we open ourselves to new impressions and new people, and moving places is one way to do that. It brings out the most creative side in scientists.</p>

<p>A colleague once pointed Sven to an old MoMA press release about "The Long Run"—about progress in art, but applicable to science. It connects to the "standing on the shoulders of giants" idea: sustained attention over time as a means of progress, rather than sudden breakthroughs. While moments of brilliance certainly exist, science works like compound interest—small consistent efforts add up to something much bigger over time. This is something he emphasizes when mentoring students.</p>
```

### Publications

```html
<p><strong>Ullrich, S.</strong>; George, J.; Coram, A. E.; Morewood, R.; Nitsche, C. "Biocompatible and selective generation of bicyclic peptides" <em>Angew. Chem. Int. Ed.</em> <strong>2022</strong>, 61, e202208400. <a href="https://doi.org/10.1002/anie.202208400">DOI</a></p>
<p class="pub-note">His first paper in a top chemistry journal, with a German-language version. The novel amino acids developed for solid-phase peptide synthesis are now commercially available from IRIS Biotech.</p>

<p><strong>Ullrich, S.</strong>*; Panda, B.; Somathilake, U.; Lawes, D. J.; Nitsche, C.* "Non-symmetric cysteine stapling in native peptides and proteins" <em>Chem. Commun.</em> <strong>2025</strong>, 61, 933–936. <a href="https://doi.org/10.1039/D4CC04995K">DOI</a></p>
<p class="pub-note">His first research paper as co-corresponding author, expanding cyanopyridine-based cyclization strategies toward fully natural peptides and proteins.</p>

<p><strong>Ullrich, S.</strong>; Ekanayake, K. B.; Otting, G.; Nitsche, C. "Main protease mutants of SARS-CoV-2 variants remain susceptible to nirmatrelvir" <em>Bioorg. Med. Chem. Lett.</em> <strong>2022</strong>, 62, 128629.</p>
<p class="pub-note">Picked up by health authorities to inform public policy. Retweeted by German Health Minister Karl Lauterbach and Dr. Eric Topol of Scripps. Published as Omicron emerged, contributing to science communication about COVID-19 drug development.</p>
```

### Recognition

```html
<h4>Fellowships</h4>
<p><strong>Feodor Lynen Research Fellowship</strong>, Alexander von Humboldt Foundation</p>

<h4>Doctoral Awards (2024)</h4>
<ul>
    <li><strong>John A. Carver Medal</strong>, Royal Australian Chemical Society — State-wide recognition for most outstanding PhD thesis in chemistry</li>
    <li><strong>Sir John Cornforth Medal</strong>, RACI — Nation-wide recognition for most outstanding PhD thesis in chemistry</li>
    <li><strong>JG Crawford Medal Runner-up</strong>, Australian National University — University-wide recognition</li>
</ul>

<h4>Conference Awards</h4>
<ul>
    <li><strong>Elizabeth A. Schram Poster Presentation Award</strong>, 27th American Peptide Symposium, Whistler, Canada (2022)</li>
</ul>

<h4>Conference Presentations</h4>
<ul>
    <li>Young Investigator Talk, 29th American Peptide Symposium, San Diego (2024)</li>
    <li>Flash Talk, 27th American Peptide Symposium, Whistler (2022)</li>
</ul>

<p>Sven appreciates the direction APS has taken in opening more talk slots to scientists in training and early career stages.</p>
```

### Reflections

**why_peptide_science**:
```html
<p>Sven made his first peptide in a lab class taught by Prof. Mier and Prof. Klein at the University of Heidelberg as an undergraduate. A brief research project with Prof. Wink on peptide natural products from the American bullfrog deepened his interest.</p>

<p>But amino acids themselves had fascinated him since high school, where he had great science teachers. He remembers one teacher, Ms. Jaeger, who showed the class how amino acids connect to proteins. Using the amino acid alphabet, she let them dream up their own polymer proteins by drawing chemical structures of polypeptides on paper—which to his teenage self felt really cool.</p>
```

**mentor_acknowledgments**:
```html
<p><strong>Christoph Nitsche</strong> (Australian National University) provided countless opportunities and always supported Sven's development as a scientist. Joining the Nitsche Lab for his PhD—rather than returning to Germany during 2020—opened many doors and interesting paths.</p>

<p><strong>Hiroaki Suga</strong> (University of Tokyo) is always supportive of exploring new ideas in the lab. Sven values the academic freedom, opportunities, and incredible hospitality—including invitations to Professor Suga's homes in Tokyo, Hawaii, Japan, and Oxford during lab visits.</p>

<p><strong>Jörg Rademann</strong> (Freie Universität Berlin) and <strong>Gottfried Otting</strong> (Australian National University) also provided valued mentorship and collaboration opportunities.</p>
```

**advice_to_students**:
> Do it! Any experience working or studying in a different country, outside your familiar environment and comfort zone, is enriching. Although it is never easy, I highly recommend it. Bonus points if you can take the time to learn a new language, which will greatly improve your quality of life.

### Beyond the Bench

**personal_interests**:
> Sports enthusiast who enjoys basketball and soccer, recently competing in the University of Tokyo Chemistry Department tournament. Follows the German national soccer team. In Tokyo, discovering new ramen styles with friends has become a favorite activity, and visiting local sento bathhouses a relaxing part of embracing the Tokyo lifestyle.

**personal_story**:
> Some people find it odd, but Sven doesn't usually consume media in large quantities. When he does engage deeply, it's with something like "You" on Netflix or the "Three-Body Problem" book series by Cixin Liu.

---

## URL Routing

Add to `urls.py`:

```python
from postdocs.views import postdoc_detail

urlpatterns = [
    # ...
    path('postdocs/<slug:slug>/', postdoc_detail, name='postdoc_detail'),
]
```

## Views

File: `postdocs/views.py`

```python
from django.shortcuts import render, get_object_or_404
from .models import PostdocProfile

def postdoc_detail(request, slug):
    postdoc = get_object_or_404(PostdocProfile, slug=slug)
    return render(request, 'postdocs/postdoc_detail.html', {'postdoc': postdoc})
```

---

## Homepage Integration

In your homepage template, query featured postdocs:

```python
# In view or context processor
featured_postdocs = PostdocProfile.objects.filter(featured_on_homepage=True)[:3]
```

```html
<section class="postdoc-highlight">
    <h2>Peptide Postdocs</h2>
    <p class="section-subtitle">Recognizing postdoctoral researchers advancing peptide science.</p>
    
    {% for postdoc in featured_postdocs %}
    <div class="postdoc-card">
        {% image postdoc.headshot fill-200x200 as thumb %}
        <img src="{{ thumb.url }}" alt="{{ postdoc.full_name }}">
        <h3>{{ postdoc.full_name }}</h3>
        <p class="affiliation">{{ postdoc.lab_name }}, {{ postdoc.institution }}</p>
        <p class="blurb">{{ postdoc.homepage_blurb }}</p>
        <a href="{% url 'postdoc_detail' postdoc.slug %}">Read more</a>
    </div>
    {% endfor %}
</section>
```

---

## Notes for Claude Code

1. Create migrations after adding the model
2. Register the snippet in admin
3. Tab JavaScript can reuse existing Global Peptide Groups implementation
4. Image uploads require Wagtail image handling
5. Consider adding a `PostdocIndexPage` if you want a Wagtail-managed listing page later
6. The Nitsche Lab reference could link to existing Lab of the Month content if available
