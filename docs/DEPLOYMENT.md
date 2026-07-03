# DEPLOYMENT.md

## Runtime

* App: Flask in `app.py`.
* Launcher: `run.sh`.
* `run.sh` sources `/var/www/blog.yas.ooo/.env` when present before starting Gunicorn.
* Gunicorn: `127.0.0.1:3299`, 2 workers, 120s timeout.
* PM2 process: `blog-yas-core`.
* VPS path: `/var/www/blog.yas.ooo`.
* Local Codex clone path: `/Users/yasyas/Library/Mobile Documents/com~apple~CloudDocs/проекты/blogcore`.
* Public dashboard: `https://blog.yas.ooo`.
* Canonical GitHub repo: `yasyarik/blogcore`.

## Commands

```bash
cd /var/www/blog.yas.ooo
python3 -m py_compile app.py
pm2 restart blog-yas-core --update-env
curl -fsS http://127.0.0.1:3299/health
```

## Nginx

* `blog.yas.ooo` vhost proxies to `http://127.0.0.1:3299`.
* Live default catchall proxies unknown Host traffic to Blog Core so external CNAME domains can be routed by Flask.
* Tracked `deploy/nginx-blog.yas.ooo.conf` contains only the `blog.yas.ooo` vhost template and does not currently include the catchall CNAME routing config.

## Environment

* `PORT`: default `3299`.
* `ADMIN_HOSTS`: default `blog.yas.ooo,127.0.0.1,localhost`.
* `CNAME_TARGET`: default `blog.yas.ooo`.
* `HOSTED_BLOG_IPS`: default `72.61.1.109`.
* `GEMINI_API_KEY` or `GOOGLE_API_KEY`: enables Gemini article generation and automatic site topic-profile inference.
* `GEMINI_TEXT_MODEL`, `GEMINI_MODEL_TEXT`, or `GEMINI_MODEL`: optional text-model override.

Do not store secrets or raw `.env` contents in this file.

## Git access notes

* VPS working copy may use SSH remote `git@github.com:yasyarik/blogcore.git`.
* Local Codex clone currently uses HTTPS remote `https://github.com/yasyarik/blogcore.git` through GitHub CLI because local SSH auth returned `Permission denied (publickey)`.

## Deployment checks

For app changes, run:

```bash
python3 -m py_compile app.py
pm2 restart blog-yas-core --update-env
curl -fsS http://127.0.0.1:3299/health
```

For nginx changes, run:

```bash
nginx -t
systemctl reload nginx
```

## Known deployment gaps

* Automated public SSL for arbitrary custom CNAME domains is not implemented yet.
* Live catchall config is server state outside the repo; document any changes here and in `CHANGELOG_AI.md`.
