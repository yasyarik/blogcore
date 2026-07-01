# PROJECT_MEMORY.md

This file is the durable memory of the project.
It must be updated after every meaningful task.

## 1. Product overview

* Project name: Blog Core for yas.ooo.
* What it does: Universal blog/content core MVP that connects external sites, scans their public design, generates a matching blog shell/preview, installs static blog pages into local site roots when available, or hosts a blog through a custom CNAME domain.
* Target users: Site owners/operators who need a blog/content factory attached to existing sites without rebuilding those sites; internally this is used to manage multiple content factories/sites from one dashboard.
* Main business goal: Provide a reusable, site-agnostic blog and article factory layer that can adapt to each connected site's design and publish SEO/content assets at scale.
* Main user flows:
  - Connect a site by homepage URL, optional brand name, and optional local webroot.
  - Scan public site design and save a theme profile.
  - Build a preview blog under `/previews/{site_id}/blog/`.
  - For local VPS sites, install static `/blog/` files into a configured webroot.
  - For external sites, configure `custom_blog_domain`, ask the client to CNAME it to `blog.yas.ooo`, enable hosted CNAME blog, and serve the blog by Host routing.
  - Manage a site's factory settings, discover topic signals, select trends/discussions, and queue article idea jobs.

## 2. Current architecture

* Frontend: Server-rendered HTML/CSS/JS strings inside `app.py`; no frontend build pipeline.
* Backend: Python Flask app in `app.py` served by Gunicorn.
* Database: SQLite at `data/blog_core.sqlite3`; `data/` is ignored and must not be committed.
* Hosting: VPS path `/var/www/blog.yas.ooo`; PM2 process `blog-yas-core` runs `run.sh`.
* Auth: No application-level auth is implemented in the MVP.
* Payments: None.
* Main external services:
  - Public site HTML/CSS fetched via `urllib.request` for design scanning.
  - Google News RSS search is used as the current Google trend/news signal source.
  - Reddit search RSS is used for discussion signals; it may rate-limit.
  - DNS resolution uses Python `socket.getaddrinfo` for CNAME/custom-domain status checks.
* Important folders/files:
  - `app.py` — Flask app, routes, SQLite schema/migrations, scanner, blog rendering, dashboard UI.
  - `run.sh` — Gunicorn launcher bound to `127.0.0.1:3299`.
  - `requirements.txt` — Flask and Gunicorn versions.
  - `deploy/nginx-blog.yas.ooo.conf` — tracked nginx vhost template for `blog.yas.ooo` only.
  - `/etc/nginx/conf.d/blog.yas.ooo.conf` — live vhost on VPS.
  - `/etc/nginx/conf.d/000-default-catchall.conf` — live catchall proxy to Blog Core for CNAME Host routing; this server file is not currently tracked in the repo.
  - `previews/` — generated preview files, ignored.
  - `docs/` — durable project memory.

## 3. Business rules

* Blog Core must support arbitrary external sites, not just sites hosted on this VPS.
* External sites should normally use hosted CNAME blog routing instead of requiring SSH/SFTP/Git/CMS access.
* Local install is only for sites whose filesystem root is available on the same VPS and configured in `root_path`.
* Deleting a connected site from the dashboard must remove only Blog Core records and preview cache. It must not delete installed `/blog` files from the target site root.
* Factory settings are per site: content context, topic strategy, languages, cadence, CNAME settings, and jobs belong to the site.
* The manage page should allow switching between connected sites without returning to the dashboard.
* Technical settings should stay compact on the site factory page; main workflow should focus on topic discovery and jobs.

## 4. Integrations

* Design scanner fetches the connected homepage URL and captures title, meta description, stylesheet URLs, inline `<style>`, body class, nav/header/footer, colors, and fonts.
* If source CSS includes native patterns `.section`, `.blog-card`, `.blog-carousel`, and `.container`, generated blog pages reuse native-looking markup.
* Hosted CNAME blog routing uses `Host` header lookup against `sites.custom_blog_domain` when `hosted_blog_enabled=1`.
* CNAME status check compares resolved custom domain IPs against `HOSTED_BLOG_IPS` or the resolved `CNAME_TARGET`.
* Topic discovery currently uses Google News RSS query with `when:{days}d`, not an official Google Trends API.
* Reddit signal fetching uses `https://www.reddit.com/search.rss`; rate limits are expected and must be handled gracefully.

## 5. SEO / content rules

* Hosted blogs serve `robots.txt` and `sitemap.xml` for the custom host.
* Current hosted sitemap includes `/blog/` and `/blog/visual-chaos-in-ai-product-cards/` only; dynamic article publishing is not fully implemented yet.
* Local install writes `sitemap-blog.xml` and appends its URL to target site's `robots.txt` when possible.
* Generated sample blog/article content is placeholder-level and should not be treated as final editorial content.
* Article ideas generated from trend/discussion signals are queued as jobs and should connect audience problems/questions to the site's offer, expertise, or editorial point of view.

## 6. Deployment

* Runtime command: `./run.sh`.
* Gunicorn binds `127.0.0.1:3299` with 2 workers and 120 second timeout.
* PM2 process name: `blog-yas-core`.
* Public dashboard domain: `https://blog.yas.ooo`.
* Live nginx `blog.yas.ooo` vhost proxies to `http://127.0.0.1:3299`.
* Live default catchall nginx config proxies unknown HTTP/HTTPS Host traffic to Blog Core so CNAME domains can be routed by the Flask app.
* Current vhost/catchall configs reference self-signed certificate paths. Automated public SSL issuance for arbitrary custom domains is not yet implemented.
* Important environment variables:
  - `PORT` default `3299`.
  - `ADMIN_HOSTS` default `blog.yas.ooo,127.0.0.1,localhost`.
  - `CNAME_TARGET` default `blog.yas.ooo`.
  - `HOSTED_BLOG_IPS` default `72.61.1.109`.
* Never store secrets or raw `.env` values in memory files.

## 7. Known pitfalls

* `data/blog_core.sqlite3` is ignored; Git commits do not preserve connected sites/jobs/theme profiles.
* `previews/` is ignored and regenerated.
* The live catchall nginx config is important for CNAME routing but is not currently represented in `deploy/nginx-blog.yas.ooo.conf`.
* HTTPS for arbitrary CNAME domains is not production-complete until certificate automation is added.
* Reddit may return `429 Too Many Requests`; UI must show disabled/error signals rather than breaking.
* Google signal source is Google News RSS search labelled in UI/code as trend/news signals; it is not official Google Trends API data.
* `install-blog` writes static files into `root_path/blog`; avoid using it for external sites with no local webroot.
* Theme scan depends on public HTML/CSS structure and may fail or capture weak design context for SPA-heavy or protected sites.

## 8. Decisions log

### 2026-07-01 — Store durable project memory in repo

* Decision: Add `AGENTS.md` and `docs/` memory files requiring Codex to read memory before non-trivial work and update changelog after each task.
* Reason: Prevent loss of project knowledge after context compaction or fresh Codex sessions.
* Files/areas affected: `AGENTS.md`, `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md`, and supporting docs.
* Replaced/deprecated: Ad hoc reliance on chat history only.

### 2026-07-01 — Use hosted CNAME blogs for external sites

* Decision: External sites should point a custom blog domain to `blog.yas.ooo`; Blog Core routes by `Host` and serves that site's blog.
* Reason: This avoids needing filesystem, Git, CMS, SSH, or SFTP access for arbitrary client sites.
* Files/areas affected: `app.py`, nginx catchall config, site settings.
* Replaced/deprecated: Assuming every site can be installed via local webroot.

### 2026-07-01 — Keep technical settings behind a gear on factory pages

* Decision: The site factory page should prioritize discovery/jobs and hide technical setup/design controls behind a settings gear.
* Reason: Factory workflow should focus on content operations, not large technical panels.
* Files/areas affected: `app.py` manage page HTML/CSS/JS.
* Replaced/deprecated: Large always-visible design/publishing panel.

## 9. Do not repeat

* Do not rely on local `/blog` installation for third-party sites; use CNAME hosting unless the local webroot is truly available.
* Do not delete installed target-site `/blog` files when removing a connected site from Blog Core.
* Do not commit SQLite database, generated previews, virtualenv, logs, or secrets.
* Do not treat Reddit availability as guaranteed; build and test degraded states.
* Do not assume chat context has all prior decisions; read memory first.
