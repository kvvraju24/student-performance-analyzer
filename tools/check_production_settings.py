"""Validate production-mode settings using a disposable, in-process secret."""
import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
os.environ.update({'DJANGO_SETTINGS_MODULE': 'config.settings', 'APP_ENV': 'production',
                   'DEBUG': 'false', 'DJANGO_SECRET_KEY': secrets.token_urlsafe(64),
                   'DJANGO_ALLOWED_HOSTS': 'validation.example.invalid'})
import django
from django.core.management import call_command

django.setup()
# This validates settings only; no server or persistent production secret is created.
call_command('check', deploy=True, fail_level='WARNING')
