# 01 · Project requirements

## Product and users
Student Performance Analyzer is a local educational analytics application. Visitors explore fictional data; authenticated analysts manage their own pseudonymous student records; an active superuser administers the local installation. A normal staff flag alone does not grant administrative access.

## Functional requirements
- Public demo: 5,000 synthetic students, ten cohorts, eight subjects, filters, group sizes, metrics, histogram, search and pagination.
- Private workspace: session login/logout, password change, record creation, per-subject score entry, paginated owned records.
- API: authenticated list, detail, creation, deletion and score updates; finite pagination and search bounds.
- CLI: validated CSV input with three required base subjects and optional additional subjects, up to twelve total; exported tables and charts.
- Integrations: expiring read-only local API credentials, deterministic two-agent pipeline, optional stdio MCP tools.

## Nonfunctional requirements
Debug stays off; no browser secrets; ownership is enforced by backend queries; passwords use Django Argon2 hashing; writes require CSRF; database constraints protect scores and uniqueness. Request bodies, pages, search terms and request rates are bounded. No cloud account, paid provider or public deployment is needed.

## Acceptance and scope
The original 1,000-row dataset must remain unchanged. Additional data must be explicitly synthetic and reproducible. Automated tests must exercise cross-user access denial, authentication, invalid scores, credential expiry and rate limits. The fifteen documents must describe implemented behavior separately from future work. Production hosting, backup restoration on another machine, remote providers, institutional permissions and a penetration test remain outside this local implementation.
