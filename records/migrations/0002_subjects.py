from django.db import migrations

def add_subjects(apps, schema_editor):
    Subject = apps.get_model('records', 'Subject')
    for name in ('Math', 'Reading', 'Writing', 'Physics', 'Chemistry', 'Biology', 'Computer Science', 'History'):
        Subject.objects.get_or_create(code=name.lower().replace(' ', '-'), defaults={'name': name})

class Migration(migrations.Migration):
    dependencies = [('records', '0001_initial')]
    operations = [migrations.RunPython(add_subjects, migrations.RunPython.noop)]
