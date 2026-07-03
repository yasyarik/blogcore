#!/usr/bin/env bash
set -euo pipefail
cd /var/www/blog.yas.ooo
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
exec .venv/bin/gunicorn --bind 127.0.0.1:3299 --workers 2 --timeout 120 app:app
