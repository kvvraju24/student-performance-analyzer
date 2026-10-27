# 15 · Errors and debugging

Keep DEBUG=false. Diagnose with test failures, local terminal output and generic HTTP status codes; never enable public tracebacks.

| Symptom | Likely cause | Safe response |
|---|---|---|
| Login rejected after bootstrap | Initial account has an unusable password | Run `manage.py changepassword local-admin` privately |
| 403 on a write | Missing/stale CSRF token, or read-only token | Reload the same-origin form; integration tokens cannot write |
| 401 from integration | Missing, expired, revoked or inactive-owner token | Issue a new short-lived token; do not log it |
| 404 for a record | Missing record or outside ownership scope | Check the current account; do not disclose another owner's data |
| 429 | Fixed-window rate exceeded | Respect Retry-After; do not rotate spoofed headers |
| 503 from API limit middleware | Database temporarily unavailable/locked | Retry after resolving the local database problem; do not bypass limits |
| 400/413 | Invalid JSON, bounds, oversized body or bad Host | Correct input; keep explicit allowed hosts |
| Missing tables | Migrations not applied | Run migrate and retry |
| Demo charts fail to load | Wrong server/path or invalid CSV | Use Django and regenerate fictional data if necessary |
| Wrong averages after adding a subject | Inconsistent headers or fixture changes | Run both Python and JavaScript suites; all discovered subjects have equal weight |
| Optional MCP import failure | Integration dependency absent/version mismatch | Install requirements-integrations.txt and rerun the protocol test |

## Incident procedure
Stop the local server if unauthorized activity is suspected. Preserve redacted event details and a private database copy. Revoke exposed tokens, change affected passwords and rotate the signing key if needed; key rotation invalidates sessions. Reproduce with a failing test, fix the narrow cause, rerun relevant suites and scans, and record the result in the audit document. Never delete history to conceal an incident or claim a clean scan proves no compromise.
