# 14 · QA and security testing

## Local commands
```sh
.venv/bin/python -m pip install -r requirements-dev.txt -r requirements-integrations.txt
.venv/bin/python -m unittest discover -s tests -v
node --test tests/dashboard.test.cjs
.venv/bin/python manage.py test records
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations --check --dry-run
.venv/bin/pip-audit -r requirements.txt
.venv/bin/pip-audit -r requirements-integrations.txt
.venv/bin/bandit -r config records integrations tools analyzer_core.py student_performance_analyzer.py -x records/tests.py
# Install gitleaks through its official release/package source first.
gitleaks git --redact --log-opts=--all
gitleaks dir --redact .
```

## Required cases
14 analysis/export tests, 8 dashboard tests and 22 Django/security/integration tests cover original and expanded data, chart generation, invalid input, CSV formulas, XSS text, pagination, CSRF, owner isolation, restricted admin access, login/logout, rate limits, body bounds, password hashes, token expiry/revocation and a real MCP-to-HTTP flow. MCP tests require the optional package and report an explicit skip if missing.

## Browser acceptance
The public demo must state synthetic provenance, show 5,000 rows and all eight subjects, filter and reset consistently, and display all score columns in its table. Anonymous workspace access must lead to login. Forms must expose labels, show errors, and never display technical tracebacks. Choose the actual local admin password privately; temporary test credentials belong only in the disposable test database.

## Limits
Static analysis, known-vulnerability scans and automated tests do not constitute a penetration test or guarantee absence of vulnerabilities. Review deployment, TLS, database backups, permissions and monitoring on the actual host before public use. Store raw audit reports privately; publish only a redacted summary.
