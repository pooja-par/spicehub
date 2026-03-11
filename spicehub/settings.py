from pathlib import Path
import os
import dj_database_url

# Build paths inside the project
BASE_DIR = Path(__file__).resolve().parent.parent

# Load environment variables from env.py if it exists
if os.path.isfile(os.path.join(BASE_DIR, 'env.py')):
    import env

# Security Settings
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY is missing — set it in environment variables")

DEBUG = os.environ.get("DEBUG", "False").lower() == "true"

# --- ALLOWED HOSTS LOGIC ---
_default_allowed_hosts = [
    '8000-poojapar-spicehub-1xer9h37ya8.ws-eu121.gitpod.io',
    'spicehub-4df0a1a6c581.herokuapp.com',
    'spicehub.onrender.com',
    'localhost',
    '127.0.0.1',
]

raw_allowed_hosts = os.getenv('ALLOWED_HOSTS', '')
if raw_allowed_hosts:
    parsed_hosts = []
    for host in raw_allowed_hosts.split(','):
        cleaned = host.strip().replace('https://', '').replace('http://', '').strip('/')
        if cleaned:
            parsed_hosts.append(cleaned)
    ALLOWED_HOSTS = parsed_hosts
else:
    ALLOWED_HOSTS = _default_allowed_hosts

# --- APPLICATION DEFINITION ---
# IMPORTANT: 'cloudinary_storage' MUST be above 'django.contrib.staticfiles'
INSTALLED_APPS = [
    'cloudinary_storage',  # Must be near the top
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'cloudinary',          # Cloudinary itself
    'django.contrib.staticfiles',
    'django.contrib.sites',
    
    # Allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    
    # Local apps
    'home',
    'products',
    'bag',
    'checkout',
    'profiles',
    'contact',
    'featured',

    # Other
    'crispy_forms',
]

SITE_ID = 1

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Essential for static files
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'allauth.account.middleware.AccountMiddleware', # Restored: Needed for newer Allauth
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'spicehub.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'templates', 'allauth'),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request', 
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.media',
                'bag.contexts.bag_contents',
                'featured.context_processors.featured_products',
            ],
            'builtins': [
                'crispy_forms.templatetags.crispy_forms_tags',
                'crispy_forms.templatetags.crispy_forms_field',
            ]
        },
    },
]

WSGI_APPLICATION = 'spicehub.wsgi.application'

# --- CRISPY FORMS ---
CRISPY_TEMPLATE_PACK = 'bootstrap4'
CRISPY_ALLOWED_TEMPLATE_PACKS = ("bootstrap4",)

# --- DATABASE ---
# Handles Render persistent disks, Local SQLite, and Postgres via DATABASE_URL
render_sqlite_path = Path('/var/data/db.sqlite3')
if render_sqlite_path.parent.exists():
    default_db_url = f"sqlite:///{render_sqlite_path}"
else:
    default_db_url = f"sqlite:///{BASE_DIR / 'db.sqlite3'}"

DATABASES = {
    "default": dj_database_url.config(
        default=default_db_url,
        conn_max_age=600,
    )
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- AUTHENTICATION / ALLAUTH ---
AUTHENTICATION_BACKENDS = (
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
)

ACCOUNT_AUTHENTICATION_METHOD = "username_email"
ACCOUNT_EMAIL_REQUIRED = True
ACCOUNT_EMAIL_VERIFICATION = "none" # Set to "mandatory" if you have SMTP working
ACCOUNT_SIGNUP_EMAIL_ENTER_TWICE = True
ACCOUNT_USERNAME_MIN_LENGTH = 4
LOGIN_URL = "/accounts/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

# --- EMAIL ---
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
DEFAULT_FROM_EMAIL = 'info@spicehub.com'

# --- STATIC & MEDIA ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Storage Logic
USE_MANIFEST_STATIC_FILES = os.getenv("USE_MANIFEST_STATIC_FILES", "False").lower() == "true"
if USE_MANIFEST_STATIC_FILES:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
else:
    STATICFILES_STORAGE = "whitenoise.storage.CompressedStaticFilesStorage"

MEDIA_URL = '/media/'
# If Cloudinary is available, use it for Media. Otherwise, local.
if os.environ.get("CLOUDINARY_URL"):
    DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
else:
    DEFAULT_FILE_STORAGE = "django.core.files.storage.FileSystemStorage"
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# --- SECURITY & CSRF ---
CSRF_TRUSTED_ORIGINS = [
    'https://8000-poojapar-spicehub-1xer9h37ya8.ws-eu121.gitpod.io',
    'https://spicehub-4df0a1a6c581.herokuapp.com',
    'https://spicehub.onrender.com',
]

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = os.getenv("SECURE_SSL_REDIRECT", "False").lower() == "true"
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# --- STRIPE ---
STRIPE_CURRENCY = "usd"
STRIPE_PUBLIC_KEY = os.getenv("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WH_SECRET = os.getenv("STRIPE_WH_SECRET", "")

# --- INTERNATIONALIZATION ---
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# --- BUSINESS LOGIC ---
FREE_DELIVERY_THRESHOLD = 30
STANDARD_DELIVERY_PERCENTAGE = 10