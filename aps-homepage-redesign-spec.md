# APS Homepage Redesign Specification

## Context

The American Peptide Society website is being rebuilt from WordPress (using Toolset plugin) to Django Wagtail. The current homepage features a carousel for research/news articles that has become suboptimal as publishing frequency has increased.

Research articles are written using the APS-MATRIX 2.1 framework and include: figure/graphic, title, lab attribution, summary blurb, publication info, and author information.

## Current Layout Issues

- Carousel in section C shows only 4 items at a time, requires user interaction
- Blurbs in carousel duplicate content on individual article pages
- Heavy visual weight relative to other homepage sections
- Poor scalability as more articles are published

## Proposed New Layout

```
┌─────────────────────────────────────────────────────────┐
│  A - Header / Navigation (no change)                    │
├─────────────────────────────────────────────────────────┤
│  B - Lab of the Month Hero Banner (no change)           │
├─────────────────────────────────────────────────────────┤
│  C - Research Grid: 4-5 compact items, horizontal row   │
│      [img+title+lab] [img+title+lab] [img+title+lab]... │
├───────────────────────────────┬─────────────────────────┤
│  LEFT COLUMN                  │  RIGHT COLUMN           │
│  Research/News items          │  Feature blocks         │
│  (continuation of C)          │  (reorderable)          │
│                               │                         │
│  • Research item              │  D - Global Peptide     │
│  • Research item              │      Labs               │
│  • Research item              │                         │
│  • Research item              │  E - Student Spotlight  │
│  • Research item              │                         │
│  • Research item              │  F - Peptide Postdocs   │
│  • Research item              │                         │
│  • Research item              │  G - General Feature    │
│                               │      (rotating)         │
├───────────────────────────────┴─────────────────────────┤
│  Footer                                                 │
└─────────────────────────────────────────────────────────┘
```

## Section Specifications

### Section C - Compact Research Grid

- 4-5 items displayed horizontally
- Each item contains ONLY:
  - Thumbnail image (the scientific figure, cropped/sized consistently)
  - Title (2-3 words)
  - Lab name (small text)
- NO blurb text (save for archive and article pages)
- Links to individual article page

### Left Column - Research River

- Continues the research/news items from section C
- 7-8 additional items
- Same compact format as section C items
- Pulls from same data source as C, just rendered vertically
- "View All Research →" link to archive at bottom

### Right Column - Feature Blocks (D, E, F, G)

| Block | Content | Update Frequency |
|-------|---------|------------------|
| D | Global Peptide Labs | Periodic |
| E | Student Spotlight | Periodic |
| F | Peptide Postdocs | Periodic |
| G | General/rotating feature | Variable |

- Blocks should be reorderable (random or preset order)
- Each block is a self-contained feature with its own editorial content
- More stable/evergreen than the research items

## Wagtail Implementation Notes

### Research Articles

C and the left column should pull from the same `ResearchArticle` queryset:
- First 4-5 items render horizontally in section C
- Remaining items render vertically in left column
- Single data source, two template treatments

Suggested model fields for `ResearchArticlePage`:
- `title` (CharField)
- `lab_name` (CharField)
- `lab_link` (ForeignKey or URL)
- `figure` (ImageField)
- `blurb` (RichTextField) - for archive/detail pages only
- `publication_title` (CharField)
- `publication_authors` (CharField)
- `publication_citation` (CharField)
- `publication_link` (URLField)
- `author_blocks` (StreamField or InlinePanel for author bios)

### Feature Blocks (D, E, F, G)

Options for implementation:
1. **StreamField on HomePage** - Most flexible for reordering
2. **Orderable InlinePanel** - Good for fixed block types
3. **Separate Snippet models** - If blocks are reused elsewhere

Each feature block type (Labs, Students, Postdocs, General) could be:
- A separate page type under a hidden index page
- A Snippet model chosen via ChooserBlock
- Inline content directly on the homepage

Reordering can be achieved via:
- `sort_order` field with drag-drop in admin
- StreamField block ordering
- Random queryset ordering in template context

### Homepage Model Sketch

```python
class HomePage(Page):
    # Section B - Lab of the Month
    lab_of_month = models.ForeignKey(
        'labs.LabPage',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    
    # Sections C + Left Column pull from ResearchArticlePage children
    # No explicit field needed - use page queryset
    
    # Right Column - Feature Blocks
    feature_blocks = StreamField([
        ('global_labs', GlobalLabsBlock()),
        ('student_spotlight', StudentSpotlightBlock()),
        ('peptide_postdocs', PostdocsBlock()),
        ('general_feature', GeneralFeatureBlock()),
    ], use_json_field=True)
    
    def get_context(self, request):
        context = super().get_context(request)
        research_articles = ResearchArticlePage.objects.live().order_by('-first_published_at')
        context['section_c_articles'] = research_articles[:5]
        context['left_column_articles'] = research_articles[5:13]
        return context
```

## Design Rationale

- **Research prominence**: Primary publishing output gets prime real estate (top + left)
- **No carousel**: 12+ articles visible without interaction
- **Scannable**: Compact format lets users quickly identify topics of interest
- **Mobile-friendly**: Two-column layout collapses naturally
- **Editorial discipline**: Feature blocks must earn their space
- **Maintainability**: Single data source for research, clear separation of concerns

## Migration Notes

Current WordPress/Toolset fields map to Wagtail as follows:
- Each Toolset field becomes a Wagtail model field
- Archive page becomes a Wagtail `IndexPage` listing `ResearchArticlePage` children
- Individual articles become `ResearchArticlePage` instances
- Flexibility is retained; display format changes, data structure stays similar

## Reference

- Current site screenshots reviewed: homepage, archive, two article detail pages
- Homepage schematic with labeled sections (A through L) reviewed
- Discussion date: December 2024
