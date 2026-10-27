# 08 · Project implementation

## Modules and responsibilities
- `analyzer_core.py`: UTF-8/BOM CSV loading, header/value validation, dynamic subjects, grading and pure summaries.
- `student_performance_analyzer.py`: CLI paths, formatted summaries, formula-safe CSV exports and headless Matplotlib reports.
- `config/`: local-first Django settings, explicit routes and WSGI entry point.
- `records/`: normalized models, schema migrations, forms, authenticated views, API access checks, rate limiting and security headers.
- `templates/`: escaped server-rendered login, private workspace, score editor and password change.
- `dashboard.js`: public synthetic CSV parsing, filters, metrics, chart/table rendering and escaping.
- `integrations/`: bounded HTTP client, read-only agent adapters and optional stdio MCP server.
- `tools/generate_demo.py`: reproducible synthetic CSV generator; manifest records the seed and limitations.

## Implementation sequence
Schema and constraints precede seed import. Authentication precedes private route exposure. Ownership queries precede serialization and writes. Form and JSON validation precede database changes. Security tests precede publication. CI checks runtime tests, dependencies, source patterns and reachable Git secrets.

## Deliberate limits
No public signup, arbitrary file upload, arbitrary SQL, browser API key, external database or model provider was added. This reduces unnecessary exposed capabilities. The original dataset and historical sample outputs remain separate regression evidence. The local database is connected and populated, but it is excluded from source control. Start.command opens a local server after prompting for the user's own password if necessary.
