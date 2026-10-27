# 06 · Agent connections

## Implemented local adapters
`integrations/agents.py` composes two deterministic roles:
1. RecordsAgent requests at most the first 100 owner-visible records through AnalyzerClient.
2. SummaryAgent computes a sample average and returns both total visible count and sample size.

The result explicitly says it describes the first page, not a full-dataset statistic. These are tested adapter roles, not autonomous LLM agents. There are no hidden provider calls, model charges, remote message sends or self-modifying actions.

## Trust and permissions
The client uses an expiring read-only API token held in the process environment. The database stores its digest only. The server rechecks owner scope, activity, expiry and revocation on every request. Tools do not accept arbitrary URLs or paths, cannot write records and do not inherit a superuser's global visibility. Never give an agent a browser session cookie or admin password.

## Run and extend
After issuing a local token, privately set ANALYZER_API_TOKEN and run `python -m integrations.agents` while the backend is running. ANALYZER_BASE_URL defaults to the loopback origin. Use distinct tokens per integration and revoke them through the admin token list when no longer needed.

Future LLM adapters must specify the provider, purpose, data retention policy and exact permitted operations. Treat returned student text as data, not instructions. External data sharing and any future write tool need explicit user intent and separate server-side authorization tests. No external agents were connected in this implementation.
