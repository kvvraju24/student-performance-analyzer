from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from records.models import Student

class Command(BaseCommand):
    help = 'Initialize the local account with an unusable password and fictional records.'
    def handle(self, *args, **options):
        if not settings.LOCAL: raise CommandError('Local bootstrap is disabled outside local mode.')
        user, created = get_user_model().objects.get_or_create(username='local-admin', defaults={'is_staff': True, 'is_superuser': True})
        if created:
            user.set_unusable_password(); user.save(update_fields=['password'])
        if not Student.objects.filter(owner=user).exists(): call_command('seed_demo', owner=user.username)
        self.stdout.write('Local data is ready. Set your password with: python manage.py changepassword local-admin')
