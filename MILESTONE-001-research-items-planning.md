# Milestone 001: Research Items Planning
**Date**: December 13, 2025
**Status**: In Discussion
**Next Step**: Resolve open questions, then build ResearchItem model

---

## Project Context

The American Peptide Society website is being rebuilt from WordPress (Toolset) to Django Wagtail. This is the second attempt - the first (`aps2026` folder) became too complex. This effort prioritizes simplicity and best practices.

### Guiding Principle
> "Get each piece rendering in a browser before building the next."

---

## Phase 1 Completed

### What's Built
- [x] Base template with Bootstrap 5, sticky nav, footer
- [x] Homepage template with "F" layout shell (3/9 configuration)
- [x] Cleaned CSS stylesheet preserving APS brand (Typekit, colors, header styles)
- [x] Development server running at localhost:8000

### The "F" Layout
```
┌─────────────────────────────────────────────────────────┐
│  NAVBAR (sticky)                                        │
├─────────────────────────────────────────────────────────┤
│  HERO / SLIDER AREA (Section B - placeholder)           │
├─────────────────────────────────────────────────────────┤
│  Latest Research                                        │
│  [1] [2] [3] [4] [5]  ← Top row: 5 newest items         │
├────────┬────────────────────────────────────────────────┤
│  [6]   │  Lab of the Month (D)                          │
│  [7]   │    [5-col text] [7-col image]                  │
│  [8]   │────────────────────────────────────────────────│
│  [9]   │  Student Spotlight (E)                         │
│  [10]  │    [5-col text] [7-col image]                  │
│  [11]  │────────────────────────────────────────────────│
│        │  Peptide Postdocs (F)                          │
│ View   │    [5-col text] [7-col image]                  │
│ All →  │────────────────────────────────────────────────│
│        │  Featured (G)                                  │
│  3-col │    [5-col text] [7-col image]        9-col     │
├────────┴────────────────────────────────────────────────┤
│  FOOTER                                                 │
└─────────────────────────────────────────────────────────┘
```

### Research Item Flow Logic
- Items ordered by publication date (newest first)
- Positions 1-5: Top horizontal row (Section C)
- Positions 6-11: Left vertical column (stem of "F")
- Position 12+: Archive only (not on homepage)
- **NO category filtering on homepage** - shows 11 most recent regardless of category
- Category filtering available on Archive page only

---

## Research Items: Why They Matter

### The Workflow
```
Weekly Scopus Search
       ↓
PhD Colleague evaluates & selects articles
       ↓
Claude (online) synthesizes/adapts article
       ↓
PI contacted for approval + photos/bios of first authors
       ↓
Published on APS site
       ↓
Social media promotion (graduate students highlighted)
```

### Organizational Importance
> "Lars has become the most important communicative instrument... who between symposia... singlehandedly keeps the society visible and engaged..." — APS Board

### Why Carousel Became Ineffective
- Only showed 4 items at a time
- Required user interaction to see more
- Publishing frequency increased beyond carousel capacity
- New "F" layout shows 11 items immediately, no interaction needed

---

## Current WordPress Toolset Fields

From `1-setup files/research_items_definition/`:

### PI Information
| Field | Type | Notes |
|-------|------|-------|
| PI First Name | Single line | |
| PI Last Name | Single line | |
| PI Title | Single line | |
| PI Institution or Business | Single line | |
| PI URL | URL | |
| Second PI Last Name | Single line | Optional |

### News Item Core
| Field | Type | Notes |
|-------|------|-------|
| News Item Title | Single line | Short display title ("Modeling Selectivity") |
| Corporate Lab | Single line | |
| News Item Blurb | Single line | Carousel teaser - may not need in F layout |
| Reflecting work in | Single line | Creates "Reflecting work in the Miller Lab" header |
| News Item Full Text | Multiple lines | The synthesized article with HTML |
| News Item Image | Image | Main figure |
| News Item Image Caption | Single line | Figure caption |

### Publication Information
| Field | Type | Notes |
|-------|------|-------|
| Publication Full Title | Single line | Full journal article title |
| Publication Authors | Single line | Author list |
| Publication Citation | Single line | Journal, year, volume, pages |
| Publication URL | URL | DOI link |

### First Author Spotlights (up to 3)
| Field | Type | Notes |
|-------|------|-------|
| Author Information | Multiple lines | Bio paragraph |
| Author Image | Image | Photo |
| Author Information Two | Multiple lines | Second author bio |
| Author Image Two | Image | |
| Author Information Three | Multiple lines | Third author bio |
| Author Image Three | Image | |

---

## Previous Wagtail Implementation (aps2026)

### Approach
- **Model Type**: Wagtail Snippet (not Page)
- **URL**: Custom view at `/news/<slug>/`
- **Admin**: SnippetViewSet with MultiFieldPanel sections
- **Features**:
  - Auto-generated slug from short_title
  - Inline image placeholders (`{{image1}}`, `{{image2}}`)
  - Category ForeignKey
  - `get_processed_content()` method for image replacement

### What Worked Well
- Clean admin form with organized sections
- Snippet approach was simpler than Page hierarchy
- Category filtering on archive page
- Auto-slug generation with duplicate handling

### What Could Improve
- Field naming was verbose (`news_item_` prefix everywhere)
- Some field purposes unclear
- Homepage blurb field may be obsolete with F layout

---

## Open Questions to Resolve

### 1. Homepage Card Display
**DECIDED**: Cards show 4 elements only

```
┌─────────────────────┐
│  [IMAGE - figure]   │
├─────────────────────┤
│  Short Title        │  ← e.g., "Modeling Selectivity"
│                     │
│  Lab Name           │  ← e.g., "Miller Lab"
│  Date               │  ← e.g., "Dec 4, 2025"
└─────────────────────┘
```

- **NO blurb on homepage** - cards are scannable, not readable
- Blurb retained for: Archive listings, Open Graph/social, search snippets
- Short title field serves as card title (no separate field needed)

### 2. Lab Name Field
**DECIDED**: Dedicated `lab_name` field

- Store clean lab name: `Miller Lab` or `Miller`
- Template can format display as needed (e.g., "the Miller Lab")
- More flexible than deriving from PI name (handles multi-PI, corporate labs)
- Replaces verbose `reflecting_work_in` from WordPress

### 3. Blurb Field
**DECIDED**: Keep field, but NOT on homepage

- **Not displayed**: Homepage F-layout cards
- **Displayed**: Archive page listings, Open Graph meta, search snippets
- Provides summary text for contexts where scanning isn't enough

### 4. Categories
**DECIDED**: 6 categories, Archive page only (not homepage)

#### Data Truncation Decision
- Original export: 232 items (2019-2025)
- **Kept**: 2025 only (87 items)
- **Rationale**: Older items have inconsistent writing quality; 2025 items use Claude synthesis

#### Category Analysis (87 items from 2025)

| Category | Count | % | Description |
|----------|-------|---|-------------|
| Synthesis & Methods | 33 | 38% | Making peptides, reactions, coupling |
| Structure & Design | 17 | 20% | Helices, macrocycles, de novo design |
| Therapeutics & Discovery | 12 | 14% | Drugs, disease targets, AMPs |
| Delivery & Penetration | 11 | 13% | Cell entry, siRNA, LYTAC |
| Natural Products & RiPPs | ~6 | 7% | Lasso, lanthipeptides, biosynthesis |
| Mechanisms & Probes | ~8 | 9% | Signaling, binding, tools |

#### Implementation Notes
- **Single primary category** per item (simpler filtering)
- Secondary tags possible later for search enhancement
- Categories used on **Archive page only** - homepage shows 11 most recent regardless
- Attempting to fill categories on homepage would be counterproductive

### 5. Architecture: Snippet vs Page
**DECIDED**: Snippet

- Matches WordPress "Custom Post" mental model
- Previous aps2026 implementation worked well
- No need for built-in preview (approval happens before data entry via email)
- SEO/Open Graph fields added manually as needed
- Custom URL routing at `/news/<slug>/`

### 6. Multiple Authors
**DECIDED**: Fixed 3 slots

- 3 author info/image pairs (matching WordPress)
- When more spotlight is warranted, create a feature block (D, E, F, G) in addition
- Feature blocks serve dual purpose: content + relationship building with labs
- Keeps admin form simple and predictable

---

## Proposed Field Structure (Draft)

Pending decisions above, here's a starting point:

```python
class ResearchItem(models.Model):  # or Page
    # === DISPLAY (Homepage F-cards) ===
    card_title = CharField(max_length=50)      # "Modeling Selectivity"
    lab_name = CharField(max_length=100)       # "Miller Lab"
    thumbnail = ForeignKey(Image)              # Main figure

    # === ARTICLE PAGE ===
    full_title = CharField(max_length=300)     # Full publication title
    blurb = TextField(blank=True)              # Optional teaser
    body = RichTextField()                     # Synthesized article
    figure_caption = TextField()               # Main image caption

    # === PUBLICATION ===
    publication_authors = CharField()
    publication_citation = CharField()
    publication_url = URLField()

    # === PI / LAB ===
    pi_first_name = CharField()
    pi_last_name = CharField()
    pi_title = CharField(blank=True)
    pi_institution = CharField()
    pi_url = URLField(blank=True)

    # === CATEGORIZATION ===
    category = ForeignKey(Category)

    # === META ===
    publish_date = DateField()
    slug = SlugField(unique=True)

# Separate model for authors (InlinePanel or fixed)
class ResearchItemAuthor(Orderable):
    research_item = ParentalKey(ResearchItem)
    name = CharField()
    bio = TextField()
    photo = ForeignKey(Image)
```

---

## Next Steps (Proposed)

1. **Resolve open questions** (discussion)
2. **Export WordPress items** for category analysis
3. **Finalize field list** based on decisions
4. **Build the model** (Snippet or Page)
5. **Create admin form** with organized panels
6. **Build detail template** for individual items
7. **Connect to homepage** (replace placeholders with real queryset)
8. **Add category filter tabs**
9. **Build archive/index page**

---

## Session Notes

- User prefers Bootstrap 3 syntax familiarity (Claude translates to BS5)
- Research items are the site's "heartbeat" between symposia
- Graduate student visibility is a key value proposition
- PI approval workflow is part of the process
- Social media sharing is important (Open Graph considerations)

---

## Category Analysis Session (December 13, 2025)

### Export & Truncation
- Exported 232 items from WordPress via WP All Export
- **Decision**: Keep only 2025 items (87 total)
- Older items (2024 and earlier) have less consistent writing quality
- 2025 items all use Claude-assisted synthesis

### Category Discussion (with Claude PRO input)

Claude PRO feedback on initial 5-category proposal:
> - Therapeutics may be undercounting (AMPs, cancer vaccines getting absorbed into Synthesis)
> - "Cell Penetration" → "Delivery & Penetration" to include siRNA, LYTAC, mitochondrial
> - Natural Products / RiPPs warrants its own category
> - "Peptide Biology" → "Mechanisms & Probes" more descriptive

**Final 6 Categories**:
1. Synthesis & Methods
2. Structure & Design
3. Delivery & Penetration
4. Therapeutics & Discovery
5. Natural Products & RiPPs
6. Mechanisms & Probes

### Key Decision
**Categories apply to Archive page only** - Homepage "F" layout shows 11 most recent items regardless of category. Attempting to populate category-filtered views on homepage would create sparse, uneven displays.

---

## Files Reference

| File | Purpose |
|------|---------|
| `aps_site/templates/base.html` | Base template with nav/footer |
| `home/templates/home/home_page.html` | Homepage F-layout |
| `aps_site/static/css/aps_site.css` | Cleaned APS styles |
| `1-setup files/existing site.html` | WordPress site documentation |
| `1-setup files/original_aps_styles.css` | Original WordPress CSS |
| `1-setup files/research_items_definition/` | Toolset fields + example article |
| `1-setup files/research_items_definition/APS-Research-Export-2025-December-13-1610.csv` | WordPress export (232 items, truncate to 87) |
| `aps-homepage-redesign-spec.md` | F-layout specification |
