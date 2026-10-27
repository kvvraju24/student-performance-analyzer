import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_http_methods
from .auth import api_auth, visible_students
from .forms import StudentForm, ScoreForm
from .models import Score, Subject

PUBLIC_FILES = {'': ('index.html', 'text/html'), 'style.css': ('style.css', 'text/css'), 'dashboard.js': ('dashboard.js', 'text/javascript'), 'data/synthetic_students.csv': ('data/synthetic_students.csv', 'text/csv'), 'docs/dashboard.png': ('docs/dashboard.png', 'image/png')}

@require_GET
def public_file(request, asset=''):
    if asset not in PUBLIC_FILES: raise Http404
    relative, content_type = PUBLIC_FILES[asset]
    return FileResponse((settings.BASE_DIR / relative).open('rb'), content_type=content_type)

@login_required
@require_http_methods(['GET', 'POST'])
def workspace(request):
    form = StudentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        student = form.save(commit=False)
        student.owner = request.user
        try:
            student.full_clean()
            student.save()
        except (ValidationError, IntegrityError):
            form.add_error('code', 'A record with this code already exists or is invalid.')
        else: return redirect('workspace')
    students = visible_students(request)
    from django.core.paginator import Paginator
    page = Paginator(students, 25).get_page(request.GET.get('page'))
    return render(request, 'workspace.html', {'form': form, 'page': page})

@login_required
@require_http_methods(['GET', 'POST'])
def edit_scores(request, pk):
    student = get_object_or_404(visible_students(request), pk=pk)
    form = ScoreForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        Score.objects.update_or_create(student=student, subject=form.cleaned_data['subject'], defaults={'value': form.cleaned_data['score']})
        return redirect('edit_scores', pk=pk)
    return render(request, 'scores.html', {'student': student, 'form': form})

def serialize(student):
    scores = {s.subject.code: s.value for s in student.scores.all()}
    return {'id': student.pk, 'code': student.code, 'cohort': student.cohort, 'scores': scores, 'average': round(sum(scores.values()) / len(scores), 2) if scores else None}

@require_http_methods(['GET', 'POST'])
@api_auth
def students_api(request):
    if request.method == 'POST':
        if request.content_type != 'application/json':
            return JsonResponse({'error': 'Expected application/json.'}, status=415)
        try:
            body = json.loads(request.body)
        except (ValueError, UnicodeError):
            return JsonResponse({'error': 'Invalid JSON.'}, status=400)
        if not isinstance(body, dict) or set(body) != {'code', 'cohort'} or not all(isinstance(v, str) for v in body.values()):
            return JsonResponse({'error': 'Supply only code and cohort as strings.'}, status=400)
        form = StudentForm(body)
        if not form.is_valid(): return JsonResponse({'errors': form.errors.get_json_data()}, status=400)
        student = form.save(commit=False); student.owner = request.user
        try:
            student.full_clean(); student.save()
        except (ValidationError, IntegrityError):
            return JsonResponse({'error': 'Record is invalid or already exists.'}, status=400)
        return JsonResponse(serialize(student), status=201)
    try:
        page = int(request.GET.get('page', 1)); size = int(request.GET.get('page_size', 25))
        if not 1 <= page <= 100000 or not 1 <= size <= 100: raise ValueError
    except ValueError:
        return JsonResponse({'error': 'page must be positive; page_size must be 1–100.'}, status=400)
    query = request.GET.get('q', '')
    if len(query) > 100: return JsonResponse({'error': 'Search is too long.'}, status=400)
    students = visible_students(request)
    if query: students = students.filter(code__icontains=query)
    count = students.count()
    return JsonResponse({'count': count, 'page': page, 'results': [serialize(s) for s in students[(page - 1) * size:page * size]]})

@require_http_methods(['GET', 'DELETE'])
@api_auth
def student_api(request, pk):
    student = get_object_or_404(visible_students(request), pk=pk)
    if request.method == 'DELETE':
        student.delete()
        return JsonResponse({'deleted': True})
    return JsonResponse(serialize(student))

@require_http_methods(['GET', 'POST'])
@api_auth
def scores_api(request, pk):
    student = get_object_or_404(visible_students(request), pk=pk)
    if request.method == 'GET': return JsonResponse(serialize(student))
    if request.content_type != 'application/json': return JsonResponse({'error': 'Expected application/json.'}, status=415)
    try: body = json.loads(request.body)
    except (ValueError, UnicodeError): return JsonResponse({'error': 'Invalid JSON.'}, status=400)
    if not isinstance(body, dict) or set(body) != {'subject', 'score'} or not isinstance(body['subject'], str) or type(body['score']) is not int:
        return JsonResponse({'error': 'Supply subject code and integer score only.'}, status=400)
    subject = Subject.objects.filter(code=body['subject']).first()
    if not subject or not 0 <= body['score'] <= 100:
        return JsonResponse({'error': 'Unknown subject or score outside 0–100.'}, status=400)
    with transaction.atomic():
        Score.objects.update_or_create(student=student, subject=subject, defaults={'value': body['score']})
    return JsonResponse(serialize(student))

@require_GET
@api_auth
def subjects_api(request):
    return JsonResponse({'results': list(Subject.objects.order_by('code').values('code', 'name'))})
