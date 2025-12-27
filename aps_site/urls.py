from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from wagtail.admin import urls as wagtailadmin_urls
from wagtail import urls as wagtail_urls
from wagtail.documents import urls as wagtaildocs_urls

from search import views as search_views
from home import views as home_views

urlpatterns = [
    path("django-admin/", admin.site.urls),
    path("admin/", include(wagtailadmin_urls)),
    path("documents/", include(wagtaildocs_urls)),
    path("accounts/", include("allauth.urls")),  # Allauth authentication
    path("membership/", include("membership.urls")),  # Membership
    path("search/", search_views.search, name="search"),
    # Research items (Peptide Publications)
    path("research/", home_views.research_archive, name="research_archive"),
    path("research/<slug:slug>/", home_views.research_item_detail, name="research_item_detail"),
    # Award recipients
    path("awards/recipient/<slug:slug>/", home_views.award_recipient_detail, name="award_recipient_detail"),
    # Static pages
    path("about/", home_views.about, name="about"),
    path("merrifield-essay/", home_views.merrifield_essay, name="merrifield_essay"),
    path("women-in-peptide-science/", home_views.women_in_peptide_science, name="women_in_peptide_science"),
    path("people/student-activities-committee/", home_views.student_activities_committee, name="student_activities_committee"),
    # In Memoriam
    path("people/in-memoriam/", home_views.in_memoriam_index, name="in_memoriam_index"),
    path("people/in-memoriam/<slug:slug>/", home_views.in_memoriam_detail, name="in_memoriam_detail"),
    # Postdoc Profiles
    path("postdocs/", home_views.postdoc_index, name="postdoc_index"),
    path("postdocs/<slug:slug>/", home_views.postdoc_detail, name="postdoc_detail"),
    # Student Spotlights
    path("students/", home_views.student_index, name="student_index"),
    path("students/<slug:slug>/", home_views.student_detail, name="student_detail"),
    # International Peptide Liaison
    path("international-peptide-liaison/", home_views.international_peptide_liaison, name="international_peptide_liaison"),
    # Symposium Proceedings
    path("proceedings/", home_views.proceedings_index, name="proceedings_index"),
    # APS Journal (Peptide Science)
    path("journal/", home_views.journal_index, name="journal_index"),
    path("journal/recent-issues/", home_views.journal_issues, name="journal_issues"),
    # Peptide Primers (Educational Content)
    path("primers/", home_views.peptide_primer_index, name="peptide_primer_index"),
    path("primers/<slug:slug>/", home_views.peptide_primer_detail, name="peptide_primer_detail"),
    # Symposia Archive (historical conference websites)
    path("symposia-archive/", home_views.symposia_archive_index, name="symposia_archive_index"),
    path("symposia-archive/<str:folder>/", home_views.symposia_archive_site, name="symposia_archive_site"),
    path("symposia-archive/<str:folder>/<path:path>", home_views.symposia_archive_site, name="symposia_archive_file"),
]


if settings.DEBUG:
    from django.conf.urls.static import static
    from django.contrib.staticfiles.urls import staticfiles_urlpatterns

    # Serve static and media files from development server
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns = urlpatterns + [
    # For anything not caught by a more specific rule above, hand over to
    # Wagtail's page serving mechanism. This should be the last pattern in
    # the list:
    path("", include(wagtail_urls)),
    # Alternatively, if you want Wagtail pages to be served from a subpath
    # of your site, rather than the site root:
    #    path("pages/", include(wagtail_urls)),
]
