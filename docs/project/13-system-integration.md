# 13 · Connecting the project parts

## Public path
Browser loads the root HTML and same-origin JavaScript/CSS, fetches only the fictional CSV, validates every required value, discovers score columns and renders all-subject metrics. The public dataset is not a database export. The existing original CSV has no Django web route.

## Private path
Login form → Django AuthenticationForm and session rotation → owner-scoped workspace queryset → normalized Student/Score/Subject tables → autoescaped HTML. Adding a score uses CSRF, a model-selected subject and an integer bound before update_or_create. Successful writes redirect to avoid accidental resubmission.

## API and integration path
Session + CSRF for writes, or read-only bearer credential → API auth decorator → active-owner scope → pagination/validation → JSON response. Agents and MCP share AnalyzerClient and therefore cannot bypass API authorization by directly opening the database. Integration clients are limited to two read endpoints.

## Offline path
CSV → analyzer_core validation and dynamic scoring → summaries → CSV reports with formula-sensitive text escaped → headless charts. Original three-subject regression results remain a separate baseline from the expanded fictional dataset.

## Failure handling
A CSV failure never falls back to private records; an API auth failure never falls back to public demo data. Missing records return 404 regardless of whether another user owns the ID. Rate database errors fail closed with 503. Invalid input is rejected before mutation; multi-score demo import is transactional. Changes to serialization, subject naming or schema must be accompanied by fixture and integration updates.
