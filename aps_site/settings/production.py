import os

from .base import *

# Load environment variables from .env file if python-dotenv is installed
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

DEBUG = False

# =============================================================================
# SECURITY SETTINGS - Critical for production
# =============================================================================

# SECRET_KEY must be set via environment variable
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY environment variable is not set. "
        "Generate one with: python -c \"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())\""
    )

# ALLOWED_HOSTS must be set via environment variable
_allowed_hosts = os.environ.get('ALLOWED_HOSTS', '')
if not _allowed_hosts:
    raise ValueError(
        "ALLOWED_HOSTS environment variable is not set. "
        "Set it to your domain(s), e.g., 'americanpeptidesociety.org,www.americanpeptidesociety.org'"
    )
ALLOWED_HOSTS = [host.strip() for host in _allowed_hosts.split(',') if host.strip()]

# =============================================================================
# HTTPS / SSL Configuration
# =============================================================================

# Redirect all HTTP requests to HTTPS
SECURE_SSL_REDIRECT = True

# Trust the X-Forwarded-Proto header from reverse proxy
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# =============================================================================
# HTTP Strict Transport Security (HSTS)
# =============================================================================

# Enable HSTS - tells browsers to only use HTTPS for 1 year
SECURE_HSTS_SECONDS = 31536000  # 1 year

# Apply HSTS to all subdomains
SECURE_HSTS_INCLUDE_SUBDOMAINS = True

# Allow preloading in browser HSTS lists
SECURE_HSTS_PRELOAD = True

# =============================================================================
# Cookie Security
# =============================================================================

# Only send session cookie over HTTPS
SESSION_COOKIE_SECURE = True

# Only send CSRF cookie over HTTPS
CSRF_COOKIE_SECURE = True

# Prevent JavaScript access to session cookie
SESSION_COOKIE_HTTPONLY = True

# =============================================================================
# Additional Security Headers
# =============================================================================

# Prevent browsers from MIME-sniffing
SECURE_CONTENT_TYPE_NOSNIFF = True

# Prevent clickjacking
X_FRAME_OPTIONS = 'DENY'

# =============================================================================
# Database Configuration
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get('DB_NAME', 'aps_wagtail_2026'),
        "USER": os.environ.get('DB_USER', ''),
        "PASSWORD": os.environ.get('DB_PASSWORD', ''),
        "HOST": os.environ.get('DB_HOST', 'localhost'),
        "PORT": os.environ.get('DB_PORT', '5432'),
    }
}

# Validate database credentials are set
if not DATABASES['default']['USER'] or not DATABASES['default']['PASSWORD']:
    raise ValueError(
        "Database credentials not set. "
        "Set DB_USER and DB_PASSWORD environment variables."
    )

# =============================================================================
# Static Files
# =============================================================================

# ManifestStaticFilesStorage is recommended in production, to prevent
# outdated JavaScript / CSS assets being served from cache
# (e.g. after a Wagtail upgrade).
# See https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#manifeststaticfilesstorage
STORAGES["staticfiles"]["BACKEND"] = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"

# =============================================================================
# DigitalOcean Spaces (S3-compatible) for Media Files
# =============================================================================

# Spaces credentials
AWS_ACCESS_KEY_ID = os.environ.get('SPACES_ACCESS_KEY')
AWS_SECRET_ACCESS_KEY = os.environ.get('SPACES_SECRET_KEY')

# Bucket configuration
AWS_STORAGE_BUCKET_NAME = os.environ.get('SPACES_BUCKET_NAME', 'aps2026-static')
AWS_S3_REGION_NAME = os.environ.get('SPACES_REGION', 'nyc3')
AWS_S3_ENDPOINT_URL = f"https://{AWS_S3_REGION_NAME}.digitaloceanspaces.com"

# Public URL for serving files (can use CDN later)
AWS_S3_CUSTOM_DOMAIN = os.environ.get(
    'SPACES_CUSTOM_DOMAIN',
    f"{AWS_STORAGE_BUCKET_NAME}.{AWS_S3_REGION_NAME}.digitaloceanspaces.com"
)

# File settings
AWS_DEFAULT_ACL = 'public-read'
AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'max-age=86400',  # 1 day cache
}
AWS_LOCATION = 'media'  # Store files in /media/ prefix in the bucket

# Use S3 for media files
STORAGES["default"]["BACKEND"] = "storages.backends.s3boto3.S3Boto3Storage"

# Update MEDIA_URL to point to Spaces
MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/{AWS_LOCATION}/"

# Validate Spaces credentials are set
if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
    raise ValueError(
        "DigitalOcean Spaces credentials not set. "
        "Set SPACES_ACCESS_KEY and SPACES_SECRET_KEY environment variables."
    )

# =============================================================================
# Wagtail Settings
# =============================================================================

# Update this to your production URL
WAGTAILADMIN_BASE_URL = os.environ.get('WAGTAILADMIN_BASE_URL', 'https://americanpeptidesociety.org')

# =============================================================================
# File Upload Limits
# =============================================================================

# Limit upload sizes to prevent DOS attacks
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

# =============================================================================
# Logging Configuration
# =============================================================================

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'django.security': {
            'handlers': ['console'],
            'level': 'WARNING',
            'propagate': False,
        },
    },
}

# =============================================================================
# Local Settings Override (optional)
# =============================================================================

try:
    from .local import *
except ImportError:
    pass
