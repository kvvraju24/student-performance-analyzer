"""Read-only local HTTP client shared by agents and MCP tools."""
import json
import os
import re
from urllib.error import HTTPError
from urllib.parse import urlencode, urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler, ProxyHandler

class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None  # Never forward an Authorization header through a redirect.

class AnalyzerClient:
    def __init__(self):
        self.base = os.environ.get('ANALYZER_BASE_URL', 'http://127.0.0.1:8000').rstrip('/')
        url = urlparse(self.base)
        if url.scheme not in {'http', 'https'} or url.hostname not in {'127.0.0.1', 'localhost', '::1'} or url.username or url.password or url.query or url.fragment or url.path:
            raise ValueError('Local integration clients accept loopback origins only.')
        self.token = os.environ.get('ANALYZER_API_TOKEN', '')
        if not re.fullmatch(r'[A-Za-z0-9_-]{43}', self.token): raise ValueError('Set ANALYZER_API_TOKEN to a generated private read-only token.')
    def get(self, route, **params):
        if route not in {'/api/students/', '/api/subjects/'}: raise ValueError('Route is not available to integrations.')
        request = Request(self.base + route + ('?' + urlencode(params) if params else ''), headers={'Authorization': 'Bearer ' + self.token, 'Accept': 'application/json'})
        try:
            with build_opener(ProxyHandler({}), NoRedirect).open(request, timeout=10) as response:
                data = response.read(1000001)
                if len(data) > 1000000: raise ValueError('Response exceeded integration size limit.')
                return json.loads(data)
        except HTTPError as error:
            raise RuntimeError(f'Analyzer returned HTTP {error.code}; check access, expiry, and rate limits.') from None
