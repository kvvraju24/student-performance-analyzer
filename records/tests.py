import hashlib
import json
import secrets
from datetime import timedelta
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import identify_hasher
from django.core.management import call_command
from django.db import IntegrityError, transaction
from django.test import Client, TestCase, override_settings
from django.utils import timezone
from .models import AccessToken, RateBucket, Student, Subject, Score

User = get_user_model()

class SecurityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.password = secrets.token_urlsafe(24)
        cls.alice = User.objects.create_user('alice', password=cls.password)
        cls.bob = User.objects.create_user('bob', password=cls.password)
        cls.staff = User.objects.create_user('staff', password=cls.password, is_staff=True)
        cls.admin = User.objects.create_superuser('root', password=cls.password)
        cls.a = Student.objects.create(owner=cls.alice, code='ALICE-1', cohort='Cohort-01')
        cls.b = Student.objects.create(owner=cls.bob, code='BOB-1', cohort='Cohort-02')
        cls.subject = Subject.objects.get(code='math')
        Score.objects.create(student=cls.a, subject=cls.subject, value=90)

    def setUp(self): self.client.force_login(self.alice)

    def test_password_is_argon2_not_plaintext(self):
        self.assertNotEqual(self.alice.password, self.password)
        self.assertEqual(identify_hasher(self.alice.password).algorithm, 'argon2')
        self.assertTrue(self.alice.check_password(self.password))

    def test_anonymous_api_and_workspace_are_protected(self):
        self.client.logout()
        self.assertEqual(self.client.get('/api/students/').status_code, 401)
        self.assertRedirects(self.client.get('/workspace/'), '/accounts/login/?next=/workspace/', fetch_redirect_response=False)

    def test_list_and_detail_enforce_owner_scope(self):
        response = self.client.get('/api/students/').json()
        self.assertEqual(response['count'], 1)
        self.assertEqual(response['results'][0]['code'], 'ALICE-1')
        for route in (f'/api/students/{self.b.pk}/', f'/api/students/{self.b.pk}/scores/', f'/workspace/students/{self.b.pk}/'):
            self.assertEqual(self.client.get(route).status_code, 404)
        self.assertEqual(self.client.delete(f'/api/students/{self.b.pk}/').status_code, 404)
        self.assertTrue(Student.objects.filter(pk=self.b.pk).exists())

    def test_score_write_cannot_cross_owner(self):
        response = self.client.post(f'/api/students/{self.b.pk}/scores/', {'subject': 'math', 'score': 10}, content_type='application/json')
        self.assertEqual(response.status_code, 404)
        self.assertFalse(Score.objects.filter(student=self.b).exists())

    def test_superuser_session_can_manage_all_records(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get('/api/students/').json()['count'], 2)
        self.assertEqual(self.client.get('/admin/').status_code, 200)

    def test_staff_and_ordinary_users_cannot_use_admin(self):
        for user in (self.alice, self.staff):
            self.client.force_login(user)
            self.assertEqual(self.client.get('/admin/').status_code, 302)
            self.assertEqual(self.client.get('/admin/auth/user/').status_code, 302)

    def test_sensitive_files_are_not_served(self):
        for path in ('/.env', '/.git/config', '/.local/db.sqlite3', '/config/settings.py', '/requirements.txt', '/StudentsPerformance.csv', '/templates/base.html', '/../../.env'):
            with self.subTest(path=path): self.assertEqual(self.client.get(path).status_code, 404)

    def test_headers_and_no_debug(self):
        response = self.client.get('/workspace/')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertIn("script-src 'self'", response['Content-Security-Policy'])
        self.assertIn("frame-ancestors 'none'", response['Content-Security-Policy'])
        self.assertEqual(response['Cache-Control'], 'no-store')
        response = self.client.get('/not-a-real-route')
        self.assertNotContains(response, 'Traceback', status_code=404)

    def test_csrf_required_for_forms_and_mutating_api(self):
        client = Client(enforce_csrf_checks=True); client.force_login(self.alice)
        self.assertEqual(client.post('/workspace/', {'code': 'NEW', 'cohort': 'Cohort-01'}).status_code, 403)
        self.assertEqual(client.post('/api/students/', {'code': 'NEW', 'cohort': 'Cohort-01'}, content_type='application/json').status_code, 403)
        client.get('/workspace/')
        token = client.cookies['csrftoken'].value
        response = client.post('/api/students/', {'code': 'NEW', 'cohort': 'Cohort-01'}, content_type='application/json', HTTP_X_CSRFTOKEN=token)
        self.assertEqual(response.status_code, 201)

    def test_payload_whitelist_and_html_validation(self):
        for body in ({'code': '<script>alert(1)</script>', 'cohort': 'A'}, {'code': 'X', 'cohort': 'A', 'owner': self.bob.pk}, {'code': [], 'cohort': 'A'}, ['wrong']):
            self.assertEqual(self.client.post('/api/students/', body, content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/students/', '{bad', content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post('/api/students/', {'code': 'X'}, content_type='text/plain').status_code, 415)

    def test_scores_validate_types_and_range(self):
        url = f'/api/students/{self.a.pk}/scores/'
        for score in (-1, 101, 2.5, True, '70'):
            self.assertEqual(self.client.post(url, {'subject': 'math', 'score': score}, content_type='application/json').status_code, 400)
        self.assertEqual(self.client.post(url, {'subject': 'math', 'score': 100}, content_type='application/json').status_code, 200)
        self.assertEqual(Score.objects.get(student=self.a, subject=self.subject).value, 100)

    def test_database_constraints(self):
        with self.assertRaises(IntegrityError), transaction.atomic():
            Score.objects.create(student=self.b, subject=self.subject, value=101)
        with self.assertRaises(IntegrityError), transaction.atomic():
            Score.objects.create(student=self.a, subject=self.subject, value=70)

    def test_pagination_and_search_limits(self):
        for query in ('?page=0', '?page_size=101', '?page=abc', '?q=' + 'a' * 101):
            self.assertEqual(self.client.get('/api/students/' + query).status_code, 400)
        response = self.client.get('/api/students/', {'q': "' OR 1=1 --"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['count'], 0)

    @override_settings(API_RATE_LIMIT=2)
    def test_rate_limiting_ignores_spoofed_forwarded_ip(self):
        self.assertEqual(self.client.get('/api/students/', HTTP_X_FORWARDED_FOR='1.1.1.1').status_code, 200)
        self.assertEqual(self.client.get('/api/students/', HTTP_X_FORWARDED_FOR='2.2.2.2').status_code, 200)
        response = self.client.get('/api/students/', HTTP_X_FORWARDED_FOR='3.3.3.3')
        self.assertEqual(response.status_code, 429)
        self.assertIn('Retry-After', response)

    @override_settings(LOGIN_RATE_LIMIT=2)
    def test_login_bruteforce_limit(self):
        self.client.logout()
        for _ in range(2): self.client.post('/accounts/login/', {'username': 'alice', 'password': 'wrong'})
        self.assertEqual(self.client.post('/accounts/login/', {'username': 'alice', 'password': 'wrong'}).status_code, 429)

    def test_login_and_logout_and_external_next(self):
        client = Client(enforce_csrf_checks=True)
        client.get('/accounts/login/'); csrf = client.cookies['csrftoken'].value
        response = client.post('/accounts/login/', {'username': 'alice', 'password': self.password, 'next': 'https://example.com/'}, HTTP_X_CSRFTOKEN=csrf)
        self.assertRedirects(response, '/workspace/', fetch_redirect_response=False)
        self.assertTrue(client.cookies['sessionid']['httponly'])
        self.assertEqual(client.cookies['sessionid']['samesite'], 'Lax')
        self.assertEqual(client.get('/accounts/logout/').status_code, 405)
        csrf = client.cookies['csrftoken'].value
        self.assertEqual(client.post('/accounts/logout/', HTTP_X_CSRFTOKEN=csrf).status_code, 302)
        self.assertEqual(client.get('/api/students/').status_code, 401)

    def test_readonly_token_scope_revocation_and_expiry(self):
        raw = secrets.token_urlsafe(32)
        token = AccessToken.objects.create(owner=self.bob, name='test', digest=hashlib.sha256(raw.encode()).hexdigest(), expires_at=timezone.now() + timedelta(hours=1))
        self.client.logout()
        headers = {'HTTP_AUTHORIZATION': 'Bearer ' + raw}
        response = self.client.get('/api/students/', **headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['results'][0]['code'], 'BOB-1')
        self.assertEqual(self.client.get(f'/api/students/{self.a.pk}/', **headers).status_code, 404)
        self.assertEqual(self.client.post('/api/students/', {'code': 'NEW', 'cohort': 'A'}, content_type='application/json', **headers).status_code, 403)
        token.revoked = True; token.save()
        self.assertEqual(self.client.get('/api/students/', **headers).status_code, 401)
        token.revoked = False; token.expires_at = timezone.now() - timedelta(seconds=1); token.save()
        self.assertEqual(self.client.get('/api/students/', **headers).status_code, 401)
        self.assertNotEqual(token.digest, raw)

    def test_superuser_token_does_not_get_global_scope(self):
        raw = secrets.token_urlsafe(32)
        AccessToken.objects.create(owner=self.admin, name='test', digest=hashlib.sha256(raw.encode()).hexdigest(), expires_at=timezone.now() + timedelta(hours=1))
        self.client.logout()
        self.assertEqual(self.client.get('/api/students/', HTTP_AUTHORIZATION='Bearer ' + raw).json()['count'], 0)

    def test_oversized_body(self):
        response = self.client.post('/api/students/', 'a' * 17000, content_type='application/json')
        self.assertEqual(response.status_code, 413)

    def test_public_demo_and_subject_catalog(self):
        self.assertEqual(Subject.objects.count(), 8)
        self.assertEqual(self.client.get('/').status_code, 200)
        self.assertEqual(self.client.get('/data/synthetic_students.csv').status_code, 200)
        self.assertEqual(len(self.client.get('/api/subjects/').json()['results']), 8)
