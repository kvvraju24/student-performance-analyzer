from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from analyzer_core import read_students
from records.models import Student, Subject, Score

class Command(BaseCommand):
    help = 'Import fictional demo students for an existing user; refuses non-empty ownership scopes.'
    def add_arguments(self, parser): parser.add_argument('--owner', required=True)
    @transaction.atomic
    def handle(self, *args, **options):
        try: owner = get_user_model().objects.get(username=options['owner'], is_active=True)
        except get_user_model().DoesNotExist as error: raise CommandError('Choose an existing active account.') from error
        if Student.objects.filter(owner=owner).exists(): raise CommandError('This user already has records; refusing to duplicate or replace data.')
        rows = read_students(settings.BASE_DIR / 'data/synthetic_students.csv')
        subjects = {name: Subject.objects.get_or_create(code=name.lower().replace(' ', '-'), defaults={'name': name})[0] for name in rows[0]['scores']}
        students = Student.objects.bulk_create([Student(owner=owner, code=row['student_id'], cohort=row['cohort']) for row in rows])
        Score.objects.bulk_create([Score(student=student, subject=subjects[name], value=value) for student, row in zip(students, rows) for name, value in row['scores'].items()], batch_size=500)
        self.stdout.write(self.style.SUCCESS(f'Imported {len(students)} synthetic students and {len(subjects)} subjects.'))
