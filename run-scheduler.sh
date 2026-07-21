#!/usr/bin/env bash
set -euo pipefail
cd /var/www/blog.yas.ooo
if [ -f .env ]; then
  set -a
  # shellcheck disable=SC1091
  source .env
  set +a
fi
exec .venv/bin/python scheduler.py
