# 05 · API integration contract

Base URL: `http://127.0.0.1:8000` for local use. Responses are JSON on successful API requests. Framework errors such as a missing object may be HTML; clients must check HTTP status before decoding. No cross-origin access is enabled.

| Endpoint | Methods | Behavior |
|---|---|---|
| `/api/students/` | GET | Owned records; `page` 1–100000, `page_size` 1–100; optional `q` up to 100 characters |
| `/api/students/` | POST | Create with exactly string fields `code` and `cohort` |
| `/api/students/{id}/` | GET, DELETE | Read or delete a visible record |
| `/api/students/{id}/scores/` | GET, POST | Read scores; write exactly `subject` code and integer `score` 0–100 |
| `/api/subjects/` | GET | Available code/name pairs |

A list response contains `count`, `page`, and `results`; a student contains `id`, `code`, `cohort`, `scores` and `average`. Empty scores produce a null average, not zero. Student codes are 1–32 ASCII letters/digits/underscore/hyphen. Cohorts add spaces and allow up to 40 characters. Owner fields and unexpected fields are rejected. All scores have equal weight.

## Authentication and errors
Browsers use Django sessions; writes also require a valid CSRF token from the same origin. Local integration clients send a Bearer token, which is read-only and owner-scoped even when issued to a superuser. Unauthorized credentials yield 401; prohibited writes 403; unseen records 404; malformed input 400; unsupported content type 415; excessive body size 413 or Django's early 400; rate limits 429 with Retry-After. The default rate is 120 requests per IP/minute, shared with workspace writes.

No external API key, remote API provider or data export destination has been configured. `integrations/client.py` permits only loopback origins, two explicit read endpoints, no redirects, ten-second timeout and a bounded response.
