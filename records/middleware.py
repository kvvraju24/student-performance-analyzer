import hashlib
import time
from datetime import timedelta
from django.conf import settings
from django.db import DatabaseError
from django.db.models import F
from django.http import JsonResponse
from django.utils import timezone
from .models import RateBucket

class ResponseSecurityMiddleware:
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        response = self.get_response(request)
        # Legacy chart bars use numeric style attributes. Scripts remain same-origin only.
        response['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; img-src 'self'; connect-src 'self'; font-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'"
        response['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=(), payment=()'
        if request.path.startswith(('/api/', '/workspace/', '/accounts/', '/admin/')):
            response['Cache-Control'] = 'no-store'
        return response

class RateLimitMiddleware:
    """Database-backed fixed windows; never trust client-supplied forwarding headers."""
    def __init__(self, get_response): self.get_response = get_response
    def __call__(self, request):
        api = request.path.startswith('/api/')
        login = request.method == 'POST' and request.path in {'/accounts/login/', '/admin/login/'}
        form_write = request.method == 'POST' and request.path.startswith(('/workspace/', '/accounts/password_change/'))
        if not (api or login or form_write): return self.get_response(request)
        if request.META.get('CONTENT_LENGTH', '').isdigit() and int(request.META['CONTENT_LENGTH']) > settings.DATA_UPLOAD_MAX_MEMORY_SIZE:
            return JsonResponse({'error': 'Request body too large.'}, status=413)
        window = 900 if login else 60
        limit = settings.LOGIN_RATE_LIMIT if login else settings.API_RATE_LIMIT
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        identities = [f'ip:{ip}']
        if login:
            identities.append('account:' + request.POST.get('username', '').strip().casefold()[:150])
        now = timezone.now()
        try:
            for identity in identities:
                key = hashlib.sha256(f'{login}:{identity}:{int(time.time()) // window}'.encode()).hexdigest()
                RateBucket.objects.get_or_create(key=key, defaults={'expires_at': now + timedelta(seconds=window * 2)})
                RateBucket.objects.filter(key=key).update(count=F('count') + 1)
                if RateBucket.objects.get(key=key).count > limit:
                    response = JsonResponse({'error': 'Too many requests. Try again later.'}, status=429)
                    response['Retry-After'] = str(window - int(time.time()) % window)
                    return response
        except DatabaseError:
            return JsonResponse({'error': 'Service temporarily unavailable.'}, status=503)
        return self.get_response(request)
