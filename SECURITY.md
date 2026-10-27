# Security policy

This project is a local demonstration, not a certified or hosted production service. Keep dependencies current and run the checks documented in [QA testing](docs/project/14-qa-testing.md). See the [audit](docs/security-audit.md) for scope, findings and remaining risks.

Do not post passwords, tokens, cookies, personal student data or private database files in public issues. Report a suspected vulnerability privately to the repository owner through a private GitHub security advisory if that facility is available. No external security reporting service has been configured.

If a secret leaks, revoke or rotate it first. Deleting it from the current source tree or history does not revoke it. Restore a private backup and invalidate affected sessions/tokens as appropriate.

The backend deliberately permits local HTTP development. Before public hosting, review HTTPS, Secure cookies, host/origin configuration, MFA for privileged accounts, proxy IP handling, production database settings, backup restoration and monitoring. Do not use Python's generic directory server for the repository containing this backend.
