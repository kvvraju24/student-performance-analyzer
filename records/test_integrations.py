import asyncio
import hashlib
import importlib.util
import os
import secrets
import sys
from datetime import timedelta
from unittest import skipUnless
from unittest.mock import patch
from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import LiveServerTestCase
from django.utils import timezone
from .models import AccessToken, Score, Student, Subject
from integrations.client import AnalyzerClient

@skipUnless(importlib.util.find_spec('mcp'), 'Install requirements-integrations.txt to test the optional MCP transport.')
class LocalIntegrationTests(LiveServerTestCase):
    def test_agents_and_mcp_use_real_authenticated_http_api(self):
        owner = get_user_model().objects.create_user('integration-owner')
        other = get_user_model().objects.create_user('other-owner')
        student = Student.objects.create(owner=owner, code='OWNED', cohort='Cohort-01')
        Student.objects.create(owner=other, code='HIDDEN', cohort='Cohort-02')
        subject = Subject.objects.get(code='math')
        Score.objects.create(student=student, subject=subject, value=80)
        raw = secrets.token_urlsafe(32)
        AccessToken.objects.create(owner=owner, name='test', digest=hashlib.sha256(raw.encode()).hexdigest(), expires_at=timezone.now() + timedelta(hours=1))
        with patch.dict(os.environ, {'ANALYZER_API_TOKEN': raw, 'ANALYZER_BASE_URL': self.live_server_url}):
            from integrations.agents import run_pipeline
            self.assertEqual(run_pipeline()['sample_average'], 80)
            async def check_mcp():
                from mcp.client.stdio import stdio_client, StdioServerParameters
                from mcp.client.session import ClientSession
                params = StdioServerParameters(command=sys.executable, args=['-m', 'integrations.mcp_server'], cwd=str(settings.BASE_DIR), env={**os.environ})
                async with stdio_client(params) as streams:
                    async with ClientSession(*streams) as session:
                        await session.initialize()
                        tools = await session.list_tools()
                        self.assertEqual({t.name for t in tools.tools}, {'list_students', 'list_subjects', 'summarize_first_page'})
                        result = await session.call_tool('list_students', arguments={'page': 1, 'page_size': 25})
                        self.assertFalse(result.is_error)
                        self.assertIn('OWNED', str(result))
                        self.assertNotIn('HIDDEN', str(result))
            asyncio.run(check_mcp())

    def test_integration_url_restrictions(self):
        for url in ('https://example.com', 'http://localhost@evil.example', 'file:///etc/passwd', 'http://127.0.0.1/path', 'http://127.0.0.1?key=value'):
            with self.subTest(url=url), patch.dict(os.environ, {'ANALYZER_BASE_URL': url, 'ANALYZER_API_TOKEN': 'test-only'}), self.assertRaises(ValueError):
                AnalyzerClient()
