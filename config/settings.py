"""Local-first settings; production must provide an independent secret and hosts."""
import os
import secrets
from pathlib import Path
from django.core.exceptions import ImproperlyConfigured

BASE_DIR = Path(__file__).resolve().parent.parent
APP_ENV = os.environ.get('APP_ENV', 'local')
if APP_ENV not in {'local', 'production'}:
    raise ImproperlyConfigured('APP_ENV must be local or production.')
LOCAL = APP_ENV == 'local'
DEBUG = False
if os.environ.get('DEBUG', 'false').lower() not in {'false', '0'}:
    raise ImproperlyConfigured('Debug mode is disabled for this project.')
PRIVATE_DIR = BASE_DIR / '.local'
PRIVATE_DIR.mkdir(mode=0o700, exist_ok=True)
PRIVATE_DIR.chmod(0o700)
# New database, journal and secret files are owner-only.
os.umask(0o077)
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', '')
if not SECRET_KEY and LOCAL:
    secret_file = PRIVATE_DIR / 'secret_key'
    try:
        with secret_file.open('x') as file:
            file.write(secrets.token_urlsafe(64))
    except FileExistsError:
        pass
    secret_file.chmod(0o600)
    SECRET_KEY = secret_file.read_text().strip()
if len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('Set a random DJANGO_SECRET_KEY of at least 50 characters.')
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]'] if LOCAL else [h.strip() for h in os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',') if h.strip()]
if not ALLOWED_HOSTS or '*' in ALLOWED_HOSTS:
    raise ImproperlyConfigured('Explicit DJANGO_ALLOWED_HOSTS values are required.')
CSRF_TRUSTED_ORIGINS = [v.strip() for v in os.environ.get('DJANGO_CSRF_TRUSTED_ORIGINS', '').split(',') if v.strip()]
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'records']
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'records.middleware.ResponseSecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'records.middleware.RateLimitMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]
ROOT_URLCONF = 'config.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [BASE_DIR / 'templates'], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'config.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': PRIVATE_DIR / 'db.sqlite3', 'OPTIONS': {'timeout': 10}}}
PASSWORD_HASHERS = ['django.contrib.auth.hashers.Argon2PasswordHasher', 'django.contrib.auth.hashers.PBKDF2PasswordHasher']
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 12}},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/workspace/'
LOGOUT_REDIRECT_URL = '/'
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_SAMESITE = 'Lax'
SESSION_COOKIE_SECURE = not LOCAL
CSRF_COOKIE_SECURE = not LOCAL
SESSION_COOKIE_AGE = 3600
SESSION_SAVE_EVERY_REQUEST = False
SECURE_SSL_REDIRECT = not LOCAL
SECURE_HSTS_SECONDS = 31536000 if not LOCAL else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = not LOCAL
SECURE_HSTS_PRELOAD = not LOCAL
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = 'same-origin'
X_FRAME_OPTIONS = 'DENY'
DATA_UPLOAD_MAX_MEMORY_SIZE = 16384
DATA_UPLOAD_MAX_NUMBER_FIELDS = 40
FILE_UPLOAD_MAX_MEMORY_SIZE = 0
STATIC_URL = '/static/'
STATIC_ROOT = PRIVATE_DIR / 'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
USE_TZ = True
TIME_ZONE = 'UTC'
API_RATE_LIMIT = 120
LOGIN_RATE_LIMIT = 10
# Public demo data is synthetic. Private database files have no serving route.
