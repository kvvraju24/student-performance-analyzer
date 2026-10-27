import hashlib
from functools import wraps
from django.http import JsonResponse
from django.utils import timezone
from .models import AccessToken

def api_auth(view):
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        request.token_authenticated = False
        header = request.headers.get('Authorization', '')
        if header:
            if not header.startswith('Bearer ') or len(header) > 256:
                return JsonResponse({'error': 'Invalid credentials.'}, status=401)
            digest = hashlib.sha256(header[7:].encode()).hexdigest()
            token = AccessToken.objects.select_related('owner').filter(digest=digest, revoked=False, expires_at__gt=timezone.now(), owner__is_active=True).first()
            if token is None:
                return JsonResponse({'error': 'Invalid credentials.'}, status=401)
            # Bearer credentials are deliberately read-only, even for a superuser.
            if request.method not in {'GET', 'HEAD', 'OPTIONS'}:
                return JsonResponse({'error': 'Integration tokens are read-only.'}, status=403)
            request.user = token.owner
            request.token_authenticated = True
        if not request.user.is_authenticated or not request.user.is_active:
            return JsonResponse({'error': 'Authentication required.'}, status=401)
        return view(request, *args, **kwargs)
    return wrapped

def visible_students(request):
    from .models import Student
    students = Student.objects.prefetch_related('scores__subject')
    # Integration tokens never inherit global administrative visibility.
    return students if request.user.is_superuser and not getattr(request, 'token_authenticated', False) else students.filter(owner=request.user)
