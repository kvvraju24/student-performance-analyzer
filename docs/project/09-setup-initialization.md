# 09 · Setup and initialization

## Mac setup
Use Python 3.11+ and Node 22+ for JavaScript tests.

```sh
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python manage.py migrate
.venv/bin/python manage.py bootstrap_local
.venv/bin/python manage.py changepassword local-admin
.venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
```

Choose a unique password in the terminal prompt; do not paste it into chat, source code or a config file. Bootstrap creates an unusable password, never a default password. After initial dependency installation, double-click Start.command as an alternative: it initializes the database, prompts only when no password exists, and opens the workspace.

## Configuration
No environment variables are required locally. A random signing key is generated into ignored `.local/secret_key`. `.env.example` documents names only; Django does not automatically load `.env`. APP_ENV is local or production. DEBUG must remain false. In production, explicit allowed hosts and a separate 50+ character signing key are required, HTTPS and Secure cookies are enabled, and runserver must be replaced with a production server. This repository's current database/operations setup is for local use.

## Optional integration and development packages
Install `requirements-integrations.txt` for MCP and `requirements-dev.txt` for auditing. Neither is required just to run the app. Run `python manage.py check` before starting and `python manage.py check --deploy` against production settings before any deployment. Never serve the repository with a generic directory server once it contains a private backend; use Django's routed server.
