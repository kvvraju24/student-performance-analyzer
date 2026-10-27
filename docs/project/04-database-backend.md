# 04 · Database and backend connection

## Implemented connection
Django connects to SQLite at `.local/db.sqlite3`. The directory is mode 0700 and new files are owner-only via the application umask. The database and generated signing secret are ignored by Git and have no HTTP serving route. No external database credentials are needed.

## Relational schema
- Django User, Group, Permission, Session: established authentication storage.
- Student: owner foreign key, pseudonymous code, cohort, creation timestamp; unique `(owner, code)`.
- Subject: unique subject code and display name; eight initial subjects are inserted by migration.
- Score: student and subject foreign keys, whole-number value; unique `(student, subject)` and database check `0 <= value <= 100`.
- AccessToken: owner, name, SHA-256 digest, expiry and revocation; never the raw bearer secret.
- RateBucket: hashed identity/window key, atomic counter and expiry index.

## Lifecycle
Run `python manage.py migrate`, then `python manage.py bootstrap_local`. Bootstrap seeds 5,000 fictional records and 40,000 scores once for `local-admin`; its password is unusable until chosen locally. Seed refuses nonempty owner scopes rather than replacing records. Subject deletion is protected when scores reference it; owner deletion cascades that owner's records.

## Operations
Use Django ORM and parameter binding, not interpolated SQL. Run `purge_expired_security_data` and Django `clearsessions` regularly. Stop the local server before copying the SQLite database for a consistent private backup; protect backups like the original. Disk encryption is an operating-system responsibility and was not verified. Moving to PostgreSQL requires a reviewed configuration/migration and restored-backup test; no remote database was connected.
