import hashlib
import secrets
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from records.models import AccessToken

class Command(BaseCommand):
    help = 'Issue an expiring, read-only integration token; shown once, stored only as a digest.'
    def add_arguments(self, parser):
        parser.add_argument('--owner', required=True)
        parser.add_argument('--name', default='local-integration')
        parser.add_argument('--days', type=int, default=1)
    def handle(self, *args, **options):
        if not 1 <= options['days'] <= 30 or not 1 <= len(options['name']) <= 40: raise CommandError('Use 1–30 days and a name of 1–40 characters.')
        try: owner = get_user_model().objects.get(username=options['owner'], is_active=True)
        except get_user_model().DoesNotExist as error: raise CommandError('Choose an existing active account.') from error
        token = secrets.token_urlsafe(32)
        AccessToken.objects.create(owner=owner, name=options['name'], digest=hashlib.sha256(token.encode()).hexdigest(), expires_at=timezone.now() + timedelta(days=options['days']))
        self.stderr.write('Save privately as ANALYZER_API_TOKEN. This value is shown once; never commit it.')
        self.stdout.write(token)
