# 12 · MCP connection

## Implemented server
The optional server uses the official MCP Python SDK 2.3.0 and stdio transport. `integrations/mcp_server.py` exposes exactly three tools: list_students, list_subjects and summarize_first_page. There is no HTTP MCP listener, arbitrary URL tool, file tool, shell tool or write tool.

```sh
.venv/bin/python -m pip install -r requirements-integrations.txt
.venv/bin/python manage.py create_read_token --owner local-admin --name local-mcp --days 1
# Privately set ANALYZER_API_TOKEN to the value shown once by that command.
.venv/bin/python -m integrations.mcp_server
```

Start the Django backend in another terminal. The token must be inherited from a private process environment; do not paste it into a committed MCP configuration. ANALYZER_BASE_URL defaults to http://127.0.0.1:8000 and only loopback origins are allowed.

## Client configuration shape
Configure an MCP-capable client with the absolute command path `/absolute/path/to/student-performance-analyzer/tools/run_mcp.sh`. It changes into the repository and launches the virtual-environment interpreter. Keep credentials in that client's secret/environment facility. Different clients have different configuration schemas; no desktop client settings were silently changed.

## Verification and limitations
An integration test starts an actual stdio session, initializes the protocol, lists the three tools and calls list_students against a live authenticated HTTP API. It verifies another owner's record is absent. Token expiry, revocation and server-side scope checks still apply. No external MCP server or external model agent was connected. A local stdio host necessarily has the token assigned to that process; run only trusted clients and use a distinct short-lived credential.

Reference: https://github.com/modelcontextprotocol/python-sdk
