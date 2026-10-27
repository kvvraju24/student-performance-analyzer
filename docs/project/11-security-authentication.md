# 11 · Security and authentication layer

## Current protections
- Django session authentication; password validation and Argon2 password storage; POST logout, one-hour sessions and HttpOnly/SameSite cookies.
- Superuser-only admin admission; staff flag alone is insufficient. Ordinary users operate only on owned records. Integration tokens remain owner-scoped even for superusers.
- CSRF middleware on forms and mutating APIs. No CSRF-exempt write route or permissive CORS configuration.
- Model forms and strict JSON allowlists; integer scores and database constraints; ORM parameter binding; escaped templates/dashboard text and CSV formula neutralization.
- Debug is always false; explicit host allowlists; generic error pages; ignored owner-only local secrets/database; no arbitrary file-serving route.
- CSP, no framing, nosniff, restrictive browser permissions and no-store for sensitive routes. CSP permits inline styles for numeric chart widths, but no inline scripts.
- Database-backed fixed-window rate limits: login 10/IP and normalized account per 15 minutes, APIs/workspace writes 120/IP/minute. Forwarding headers are not trusted.
- Local API tokens contain random high-entropy material, expire in 1–30 days, are read-only and stored as digests. This fast digest is for random tokens, not human passwords.

## Local versus production
HTTP is permitted only for loopback development; secure-cookie flags and HSTS/HTTPS redirect turn on in production mode. No admin MFA, public edge protection, centralized monitoring, PostgreSQL connection, backup restoration or live TLS endpoint has been verified. Do not expose runserver or use generic directory serving. A reverse proxy needs a reviewed client-IP policy; otherwise shared proxy IPs share one rate bucket.

## Credential response
No matching secrets were found by the repository scans performed. This is not proof no secret exists. If a credential is ever exposed, revoke/rotate it at its provider first. Removing a file or rewriting history alone cannot revoke a leaked credential. Never print environment values, token bodies, cookies or passwords in logs or public issues.
