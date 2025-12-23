from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import ResearchItem, ResearchItemCategory, AwardRecipient, AwardType, InMemoriam, PostdocProfile, StudentProfile, Proceeding, JournalIssue


def research_item_detail(request, slug):
    """Display a single research item."""
    item = get_object_or_404(ResearchItem, slug=slug)
    return render(request, 'home/research_item_detail.html', {'item': item})


def about(request):
    """Display the About page."""
    return render(request, 'home/about.html')


def research_archive(request):
    """
    Display paginated archive of research items.
    Optional category filter via ?category=slug
    """
    items = ResearchItem.objects.all().order_by('-publish_date', '-created_at')
    categories = ResearchItemCategory.objects.all()

    # Filter by category if provided
    category_slug = request.GET.get('category')
    active_category = None
    if category_slug:
        active_category = get_object_or_404(ResearchItemCategory, slug=category_slug)
        items = items.filter(category=active_category)

    # Paginate - 12 items per page
    paginator = Paginator(items, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'home/research_archive.html', {
        'page_obj': page_obj,
        'categories': categories,
        'active_category': active_category,
    })


def award_recipient_detail(request, slug):
    """Display a single award recipient's detail page."""
    recipient = get_object_or_404(AwardRecipient, slug=slug)

    # Get all award types for sidebar navigation
    award_types = AwardType.objects.filter(is_active=True)

    return render(request, 'home/award_recipient_detail.html', {
        'recipient': recipient,
        'award_types': award_types,
        'current_award': recipient.award_type,
    })


def merrifield_essay(request):
    """Display the Merrifield Essay page."""
    return render(request, 'home/merrifield_essay.html')


def student_activities_committee(request):
    """Display the Student Activities Committee page."""
    return render(request, 'home/student_activities_committee.html')


def in_memoriam_index(request):
    """Display the In Memoriam index page."""
    people = InMemoriam.objects.all().order_by('-display_order')
    return render(request, 'home/in_memoriam_index.html', {'people': people})


def in_memoriam_detail(request, slug):
    """Display a single In Memoriam entry."""
    person = get_object_or_404(InMemoriam, slug=slug)
    # Get other people for navigation (exclude current, limit to 6)
    other_people = InMemoriam.objects.exclude(slug=slug).order_by('-display_order')[:6]
    return render(request, 'home/in_memoriam_detail.html', {
        'person': person,
        'other_people': other_people,
    })


def postdoc_index(request):
    """Display all postdoc profiles."""
    postdocs = PostdocProfile.objects.all().order_by('-publish_date')
    return render(request, 'home/postdoc_index.html', {'postdocs': postdocs})


def postdoc_detail(request, slug):
    """Display a single postdoc profile."""
    postdoc = get_object_or_404(PostdocProfile, slug=slug)
    return render(request, 'home/postdoc_detail.html', {'postdoc': postdoc})


def student_index(request):
    """Display all student spotlight profiles."""
    students = StudentProfile.objects.all().order_by('-publish_date')
    return render(request, 'home/student_index.html', {'students': students})


def student_detail(request, slug):
    """Display a single student spotlight profile."""
    student = get_object_or_404(StudentProfile, slug=slug)
    return render(request, 'home/student_detail.html', {'student': student})


def international_peptide_liaison(request):
    """Display the International Peptide Liaison page."""
    return render(request, 'home/international_peptide_liaison.html')


def proceedings_index(request):
    """Display the Symposium Proceedings archive page."""
    proceedings = Proceeding.objects.all().order_by('-year')
    return render(request, 'home/proceedings_index.html', {'proceedings': proceedings})


def journal_index(request):
    """Display the APS Journal (Peptide Science) main page with all issues."""
    # Get all issues ordered by year (descending) then month (descending)
    recent_issues = JournalIssue.objects.all().order_by('-year', '-month')
    return render(request, 'home/journal_index.html', {'recent_issues': recent_issues})


def journal_issues(request):
    """Display all journal issues."""
    issues = JournalIssue.objects.all()
    return render(request, 'home/journal_issues.html', {'issues': issues})
