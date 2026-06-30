#!/usr/bin/env bash
set -euo pipefail
cd /var/www/blog.yas.ooo
exec .venv/bin/gunicorn --bind 127.0.0.1:3299 --workers 2 --timeout 120 app:app
