#!/bin/zsh
set -eu
cd "$(dirname "$0")"
if [ ! -x .venv/bin/python ]; then
  echo 'Create the virtual environment and install requirements first; see README.md.'
  exit 1
fi
.venv/bin/python manage.py migrate --noinput
.venv/bin/python manage.py bootstrap_local
if ! .venv/bin/python manage.py shell -c 'from django.contrib.auth import get_user_model; import sys; sys.exit(0 if get_user_model().objects.get(username="local-admin").has_usable_password() else 1)' >/dev/null; then
  echo 'Choose a private local admin password. It will not appear while typing.'
  .venv/bin/python manage.py changepassword local-admin
fi
open http://127.0.0.1:8000/workspace/
exec .venv/bin/python manage.py runserver 127.0.0.1:8000 --noreload
