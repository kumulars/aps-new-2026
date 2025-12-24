import re
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary using a variable key."""
    if dictionary is None:
        return None
    return dictionary.get(key, key)


@register.filter
def fix_media_urls(content):
    """
    Replace hardcoded /media/ paths with the correct MEDIA_URL.

    This handles content entered in Wagtail admin with inline images
    that use hardcoded /media/ paths. On production, MEDIA_URL points
    to DigitalOcean Spaces, so this filter transforms the paths correctly.

    On development: /media/path → /media/path (no change)
    On production: /media/path → https://bucket.nyc3.digitaloceanspaces.com/media/path
    """
    if not content:
        return content

    media_url = getattr(settings, 'MEDIA_URL', '/media/')

    # If MEDIA_URL is not /media/, transform the paths
    if media_url != '/media/':
        # Replace src="/media/ and href="/media/ with the correct MEDIA_URL
        # Handle both double and single quotes
        content = re.sub(
            r'(src|href)=(["\'])/media/',
            rf'\1=\2{media_url}',
            str(content)
        )

    # Always mark as safe since this filter replaces |safe in templates
    return mark_safe(content)
