# Security audit · 27 October 2026

## Scope and assurance
Reviewed the repository, locally reachable Git references/history, project environment-variable handling, local Django settings, database schema/permissions, dependency declarations, private routes, forms, API authorization and optional local integrations. Exercised the implemented application with unit, browser and real HTTP/MCP integration checks. No external production URL, hosting account, provider dashboard, remote database, cloud secret store, other Mac project, unreachable Git object or third-party fork was audited.

This is an engineering security review, not a penetration-test certification or a guarantee that the application cannot be hacked. Clean scanner results cover the rules and advisory data available when run.

## Before and changes made

| Area | Initial state / finding | Implemented response |
|---|---|---|
| Backend, accounts, database | Static dashboard and offline CLI; no backend/login/database/admin existed | Local Django 5.2.18 application, migrations and normalized SQLite schema |
| Authorization | No private-record model existed | Owner-scoped record queries and mutation checks; superuser-only admin; tests deny cross-owner reads/writes/deletes |
| Passwords and sessions | No password system existed | Django Argon2 password storage and validators, session rotation, POST logout, one-hour sessions; no usable default admin password |
| Secrets and configuration | No matching external keys or environment files found in performed scans | Generated ignored local signing secret, environment-only production settings, no browser credentials; debug always off |
| File exposure | A generic repository file server would expose future private files | Django serves explicit public assets only; hidden/config/database source paths tested as 404; local admin assets are narrowly routed |
| Input handling | CSV validation and dashboard escaping existed; exports could retain formula-triggering text | Strict forms/JSON allowlists and score constraints; formula-sensitive CSV text prefixed; dynamic-subject validation |
| Abuse | No backend rate controls | Database atomic counters; login IP/account limits, API/write limits, page/search/body bounds, bounded integration responses and timeouts |
| Browser headers | No backend response-header layer | CSP, anti-framing, nosniff, Permissions-Policy and sensitive-route no-store; HTTPS/HSTS/Secure cookies in production settings |
| Dependencies | Matplotlib had an open minimum bound | Exact direct runtime versions; optional integration/audit requirements separated; vulnerability scans and pinned CI action commits |
| Agent/MCP scope | No integration existed | Local read-only token-backed API client; no redirects/proxies/arbitrary routes; stdio MCP with three read tools and expiring owner scopes |

## Evidence from this run
- Fourteen Python analysis/export tests and eight JavaScript dashboard tests pass, including original-data regression, 5,000-row/eight-subject validation and formula-safe export.
- Twenty-two Django security/integration tests pass. They include login/logout, CSRF, Argon2 verification, staff/admin separation, owner isolation, unsafe payloads, database bounds, request sizes, throttling, expired/revoked credentials and an actual MCP stdio call through the authenticated HTTP API.
- Django system checks and migration-drift check pass. `tools/check_production_settings.py` passes deployment checks using an ephemeral validation-only key and test hostname. This does not validate a real deployed host.
- Local `check --deploy` intentionally reports four warnings for loopback HTTP: HSTS, HTTPS redirect, Secure session cookie and Secure CSRF cookie are disabled locally. Production mode enables those controls. Warnings are not globally suppressed.
- pip-audit reports no known vulnerabilities in the resolved runtime or optional integration requirements. `pip check` reports no broken requirements.
- Bandit reports no findings after one narrowly documented B311 suppression for deterministic fictional-data sampling. Security tokens and signing keys use `secrets`, not that PRNG.
- Gitleaks reports no matching secrets in the scanned working tree and reachable history with `--all`, using redacted reports. Scanner output does not establish the absence of undiscovered secrets, deleted remote artifacts or credentials outside this project. No credential rotation or history rewrite was performed because no credential match was found.
- The project-specific environment names were unset in the local process. Their values were never printed. `.env.example` contains documentation only; no real `.env` was found in the project scan. Local secret and SQLite files were verified mode 0600 under a 0700 directory.
- Browser check: the demo loads 5,000 fictional records and eight subject columns. The workspace redirects an anonymous browser to the labelled login form. Private authentication/mutation behavior is additionally exercised by automated HTTP tests.

Raw scanner reports remain in ignored `security-reports/`; passwords, cookies, signing keys and real bearer credentials are not published. The original CSV remains unchanged. Generated public data contains fictional IDs and scores only.

## Remaining risks and release boundaries
1. **Local use only.** No public deployment, TLS termination, production WSGI/ASGI server, firewall, edge DoS control or production monitoring has been verified. Do not expose runserver.
2. **Privileged authentication.** Admin requires a strong locally chosen password; MFA and recovery workflows are not configured. Bootstrap leaves sign-in disabled until that password is chosen.
3. **SQLite operations.** File permissions and constraints are configured; disk encryption, separate-device backup restoration, high concurrency and database-server access policies remain unverified.
4. **Rate limits.** Fixed windows permit boundary bursts. Login limits can temporarily deny an attacked username. Proxies share one address unless a trusted proxy/client-IP policy is deliberately implemented. Expired bucket/session/token cleanup must be scheduled by the operator; no persistent background task was silently installed.
5. **CSP exception.** Inline styles are permitted for generated chart widths. Scripts remain same-origin only with no inline-script permission.
6. **Integration configuration.** MCP protocol and local API tests pass, but no external agent/provider account or desktop MCP client was configured. The agent roles are deterministic adapters, not LLM agents. Keep tokens short-lived and private.
7. **Data provenance.** New records are explicitly synthetic. Source/reuse terms for the unchanged original CSV remain unverified; the MIT code license does not resolve them.
8. **Maintenance.** Advisory databases evolve. CI and Dependabot are configured to repeat checks, but future findings require review and patches. A clean run is not proof of zero vulnerabilities.

## Reproduce and references
Follow the commands in [QA testing](project/14-qa-testing.md). Before hosting, review the [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/) and [password-management guidance](https://docs.djangoproject.com/en/5.2/topics/auth/passwords/). Django 5.2 is a supported LTS line per the [official download page](https://www.djangoproject.com/download/). The optional transport follows the [official MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk).
