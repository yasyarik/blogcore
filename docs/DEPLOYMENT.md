# DEPLOYMENT.md

## Runtime

* App: Flask in `app.py`.
* Launcher: `run.sh`.
* Gunicorn: `127.0.0.1:3299`, 2 workers, 120s timeout.
* PM2 process: `blog-yas-core`.
* VPS path: `/var/www/blog.yas.ooo`.
* Public dashboard: `https://blog.yas.ooo`.

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

Do not store secrets or raw `.env` contents in this file.

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
