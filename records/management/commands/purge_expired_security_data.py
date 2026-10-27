from django.core.management.base import BaseCommand
from django.contrib.sessions.models import Session
from django.utils import timezone
from records.models import RateBucket, AccessToken

class Command(BaseCommand):
    help = 'Delete expired rate windows, sessions, and integration credentials.'
    def handle(self, *args, **options):
        now = timezone.now()
        for model, field in ((RateBucket, 'expires_at'), (Session, 'expire_date'), (AccessToken, 'expires_at')):
            count, _ = model.objects.filter(**{field + '__lt': now}).delete()
            self.stdout.write(f'{model.__name__}: {count} expired objects removed')
