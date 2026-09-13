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

## Personal-brand media-plan routes

* Every Blog Core site has a server-owned fallback at `https://blog.yas.ooo/sites/{siteId}/media-plan`; it requires no per-site Nginx change and is linked from the Blog Core dashboard immediately after onboarding.
* To expose the same live page at `https://client-domain/media-plan`, the native site integration must proxy both `/media-plan` and `/media-plan/` to Blog Core while preserving the original Host. The renderer and data are universal; this small route handoff is still required when the client domain is served by another application.
* `https://karpaleksei.com/media-plan` and `https://veselovaveronika.com/media-plan`, together with their `/media-plan/...` form actions, proxy to Blog Core port `3299` while preserving the original Host header.
* The reusable location template is `deploy/nginx-personal-brand-media-plan.conf`. Add both its exact page location and action-prefix location to the HTTP and HTTPS server blocks; test Nginx before reloading. Proxying only the exact page route breaks rescheduling and one-way Reel completion with an upstream-site 404.
* Initial creation uses `deploy/seed_personal_brand_media_plans.py --db data/blog_core.sqlite3` and keeps an existing calendar by default. Do not use its destructive `--replace` option for editorial revisions.
* Apply the approved first-month revision with `deploy/update_personal_brand_launch_plan.py --db data/blog_core.sqlite3` as a dry run, then with `--apply` after reviewing the exact targets. It creates a SQLite online backup, retains row IDs/dates/statuses, preserves completed/unrelated rows and removes only the untouched excess Telegram plans. Repeat runs produce zero changes. Verify on a disposable database copy first and run `python3 -m unittest deploy.test_personal_brand_launch_plan -v`.
* The v5 growth revision also updates the stored KPI and `growth` metadata, plus one `growthPlan` on an existing article per batch. Deploy `media_plan_growth.py` beside `app.py` and `deploy/personal_brand_growth.py` with the editorial modules. The native calendar renders manual review dates relative to the actual start; this module does not collect analytics or schedule reports. Source recovery for the 2026-09-13 rollout: `/var/backups/blog-core/pre-growth-source-20260913`; DB recovery: `/var/backups/blog-core/pre-personal-brand-launch-20260913-123253-300656.sqlite3`.
* After application or reminder-worker changes, compile `app.py`, `scheduler.py`, `strategy_agent.py` and the seed script, restart both Blog Core PM2 processes, verify `/health`, then test both public calendar URLs at desktop and mobile widths.

## Shared carousel release check

* After changing carousel scheduling, restart both `blog-yas-core` and `blog-yas-core-scheduler`.
* Verify a due plan resolves to a `PUBLISHED` or `IMPORTED` content job before allowing generation. A synthetic `agent-social-*` identifier is not a source article.
* A plan waiting for its article is retained and must not prevent a later valid carousel plan from running.

## LaycanMatch native-factory release check

* Native factory: `/var/www/content-factory-laycanmatch`, PM2 process `content-factory-laycanmatch`, loopback port `13157`.
* After changing its V3 publisher, compile it, restart its PM2 process, then run the complete V3 build below. Do not treat a single page response as sufficient verification.

```bash
cd /var/www/content-factory-laycanmatch
.venv/bin/python3 -m py_compile app.py
pm2 restart content-factory-laycanmatch --update-env
cd /var/www/template-core-v3
python3 -m factory_v3.cli build-preview --site sites/laycanmatch/site.yaml --language en
```

## Nginx

* `blog.yas.ooo` vhost proxies to `http://127.0.0.1:3299`.
* Live default catchall proxies unknown Host traffic to Blog Core so external CNAME domains can be routed by Flask.
* Tracked `deploy/nginx-blog.yas.ooo.conf` contains only the `blog.yas.ooo` vhost template and does not currently include the catchall CNAME routing config.

### Georivo native renderer

* Application path: `/var/www/georivo-blog`.
* Service: `georivo-blog.service`.
* Loopback listener: `127.0.0.1:13340`.
* Money-page hero assets are tracked as `deploy/georivo/money-hero-*.webp`, installed at the renderer root, served through `/blog-assets/`, and preloaded by the money-page HTML.
* Public routes handled locally: `/blog`, `/guides`, `/templates`, `/examples`, `/embed`, `/use-cases`, root SEO money pages `/how-it-works`, `/coverage`, `/pricing`, their configured locale-prefixed equivalents, `/content-preview/`, and `/sitemap.xml`. EN uses unprefixed canonical paths; `/en/...` redirects to them.
* Existing Georivo product routes continue to proxy to their configured upstream.
* Tracked deployment templates live under `deploy/georivo/`.
* Nginx proxies the Blog Core-owned content paths `/blog`, `/guides`, `/templates`, `/examples`, `/embed`, `/use-cases`, `/how-it-works`, `/coverage`, `/pricing`, their configured locale-prefixed equivalents, `/content-preview/`, and `/sitemap.xml` to `127.0.0.1:13340`. All other product routes remain on the existing Georivo upstream.
* Native renderer services import shared `/var/www/blog.yas.ooo/native_site_chrome.py`; set `PYTHONPATH=/var/www/blog.yas.ooo` in their service environment.
* `georivo-content-audit.timer` runs the public content-contract audit daily at 04:15 UTC with up to 10 minutes of randomized delay. The oneshot service must finish with status `0/SUCCESS`.
* `georivo-gsc-submit.timer` runs at 04:45 UTC with up to 10 minutes of randomized delay. It validates the public sitemap, retries official Search Console submission, and refreshes aggregate search-performance plus key-URL indexation evidence.
* The GSC credential lives only at ignored `/var/www/blog.yas.ooo/keys/gsc-service-account.json` with mode `0600`. Never commit or print its private-key fields.
* GSC runtime state is ignored `/var/www/blog.yas.ooo/data/georivo-gsc-status.json`. `blocked` means the credential is valid but lacks property access; `error` means an operational failure; `submitted` is the only success state.

```bash
python3 -m py_compile /var/www/georivo-blog/app.py
python3 /var/www/blog.yas.ooo/deploy/georivo/seed_money_pages.py
systemctl restart georivo-blog
curl -fsS http://127.0.0.1:13340/health
python3 /var/www/blog.yas.ooo/deploy/georivo/audit_money_pages.py
cd /var/www/blog.yas.ooo/deploy/georivo
python3 audit_content_plan.py --check-public
systemctl list-timers --all georivo-content-audit.timer --no-pager
systemctl list-timers --all georivo-gsc-submit.timer --no-pager
nginx -t
systemctl reload nginx
```

## Environment

* `PORT`: default `3299`.
* `ADMIN_HOSTS`: default `blog.yas.ooo,127.0.0.1,localhost`.
* `CNAME_TARGET`: default `blog.yas.ooo`.
* `HOSTED_BLOG_IPS`: default `72.61.1.109`.
* `GEMINI_API_KEY` or `GOOGLE_API_KEY`: enables Gemini article generation and automatic site topic-profile inference.
* `GEMINI_TEXT_MODEL`, `GEMINI_MODEL_TEXT`, or `GEMINI_MODEL`: optional text-model override.
* `GSC_SERVICE_ACCOUNT_FILE`: optional path override for deploy scripts that submit sitemaps through Google Search Console.
* `GSC_INSPECTION_URLS`: optional comma-separated canonical URL override for the daily Search Console URL Inspection set.
* `PUBLICATION_ALERT_EMAIL_TO`: recipient for failed queued-publication alerts; if absent, failures remain pending without being discarded.
* `PUBLICATION_ALERT_EMAIL_FROM`: optional sender identity for publication alerts. Delivery uses the host's existing local sendmail/Exim configuration, shared with SoloCruz.
* Blog Core's universal GSC collector uses the same ignored `GSC_SERVICE_ACCOUNT_FILE` (or the existing service-account fallback). Grant the service account access to each configured Search Console property.

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

For GSC collector changes, restart both Blog Core processes:

```bash
python3 -m py_compile app.py scheduler.py
pm2 restart blog-yas-core --update-env
pm2 restart blog-yas-core-scheduler --update-env
```

For nginx changes, run:

```bash
nginx -t
systemctl reload nginx
```

## Known deployment gaps

* Automated public SSL for arbitrary custom CNAME domains is not implemented yet.
* Live catchall config is server state outside the repo; document any changes here and in `CHANGELOG_AI.md`.
# Central search operations (2026-08-03)

* Installed `blog-core-search-monitor.timer` for the daily read-only multi-site monitor. Its service uses a non-blocking `flock`, 15-minute timeout, 384 MB memory ceiling, 50% CPU quota, filesystem protection, and no service restart commands.
* Runtime evidence is `/var/lib/blog-core/search/georivo.json` and `/var/lib/blog-core/search/cabinjoin.json`, both root-owned mode `0600`. The manual production run completed for both sites with 1.294 CPU seconds and a 39.8 MB memory peak.
* Retired timers `georivo-content-audit.timer`, `georivo-gsc-submit.timer`, and `cabinjoin-gsc-submit.timer` were disabled and their `/etc/systemd/system` plus tracked deployment units removed. Backup: `/root/retired-search-units-20260803T173437Z`. Verify them with `systemctl show UNIT -p LoadState`; expected value is `not-found`.
* The new timer cannot reload/restart Nginx. During deployment Nginx retained PID `1098121` and its 2026-08-01 activation time. Only `blog-yas-core` and `blog-yas-core-scheduler` were explicitly restarted and health-checked.
# Reel layer pipeline environment

* `MASKED_LAYER_REEL_ENABLED=1` enables production Reel generation.
* `VERTEX_AI_SERVICE_ACCOUNT_FILE` points to the server-side service-account JSON outside Git.
* `VERTEX_AI_PROJECT`, `VERTEX_AI_LOCATION`, and `VERTEX_IMAGEN_EDIT_MODEL` select the optional native explicit-mask editor.
* Restart with `pm2 restart blog-yas-core --update-env` after changing these values, then verify `http://127.0.0.1:3299/health`.
## Reel Visual Library

* Build or refresh one site's library with `python3 rebuild_reel_asset_library.py SITE_ID` from `/var/www/blog.yas.ooo`.

## Social scheduler release checks

* Compile both deployed modules: `python3 -m py_compile app.py scheduler.py`.
* Restart both `blog-yas-core` and `blog-yas-core-scheduler`; confirm both remain `online` after the import cycle.
* Exercise active social prompt builders with a real site and published content job. Python compilation does not detect unescaped literal braces inside a runtime f-string format expression.
* For a publishing repair, verify one new creative end to end through the configured provider and record its `social_posts` row and remote provider ID.
* Source assets remain under `data/social_assets/{site_id}`. The generated catalog, manual overrides, and canonical symlinks live under `data/reel_asset_library/{site_id}` and must not be committed.
* The live review UI is `/sites/{site_id}/reel-asset-library`; it is linked from the Instagram Reels card in Distribution.
* New completed visual productions queue an asynchronous catalog refresh automatically.

## EPR Scan native content handoff

* `eprscan-blog-core-content.path` watches `/var/www/eprscan/data/blog-core/published` and `/var/www/eprscan/data/blog-core/drafts`. A draft change rebuilds only the private native preview; it does not make the article public. Publication still requires an explicit Blog Core publication and the fail-closed multilingual validator.
* The deployment service runs the EPR content sync validator, TypeScript and production build before restarting PM2 process `eprscan`. A validation failure occurs before the build and is visible in the systemd journal.
* Draft review routes use `/content-preview/{jobId}`, send `noindex`/no-store, stay outside the sitemap and serve imported media from `/images/blog-core/{jobId}/` under EPR Scan's self-only CSP.
* Verify the complete multilingual boundary with `RELEASE_BASE_URL=https://eprscan.eu RELEASE_CANONICAL_BASE_URL=https://eprscan.eu node scripts/check-blog-core-integration.mjs` from `/var/www/eprscan`. The check covers 60 translated public variants, 10 populated English directory/trust routes and 16 private routes, including fail-closed review/indexing rules and explicit RU/IT exclusion.
* Run `npm run translations:check` after localized source generation. It fails when a catalogued translation remains English in generated DE/FR/ES code, including composite JSX phrases.
* The 2026-09-02 trust/indexing release can be recovered from `/var/www/eprscan-release-backups/pre-review-index-gates-20260902-1505`; the subsequent hubs, internal-linking and analytics release from `/var/www/eprscan-release-backups/pre-seo-hubs-20260902-1252`.
* `eprscan-seo-crawl.timer` is enabled for Mondays at 06:15 UTC with `Persistent=true` and up to 30 minutes of randomized delay. It runs the multilingual integration check, release check, dynamic sitemap crawl and localization completeness check. Inspect `systemctl list-timers eprscan-seo-crawl.timer`, `/var/lib/eprscan/seo-crawl/last.json`, the NDJSON history, and `journalctl -u eprscan-seo-crawl.service`.
* The dynamic sitemap crawl checks every current indexable URL plus discovered internal targets for non-200 responses or redirects, noindex-in-sitemap, canonical mismatch, missing/duplicate metadata, H1 count, broken links, orphan pages and non-reciprocal/non-indexable hreflang targets. It therefore includes future valid Blog Core articles without a hard-coded URL list.
* Weekly-crawl deployment backup: `/var/www/eprscan-release-backups/pre-weekly-seo-crawl-20260902-1301`; pre-dynamic-crawler wrapper backup: `/var/www/eprscan-release-backups/pre-indexable-sitemap-crawl-20260902-1305`.
* EPR Scan uses direct static delivery for its already-WebP editorial images because the Vinext image endpoint redirects to the source asset instead of transforming it. Hero images are explicitly preloaded/high-priority; the production favicon is a 64px indexed PNG. Quality-fix backup: `/var/www/eprscan-release-backups/pre-quality-fix-20260902-1322`.
* `node scripts/check-lighthouse.mjs` runs three attempts per representative page by default. It gates on median Performance/LCP, the lowest Accessibility/SEO score, and maximum CLS; override only the attempt count with `QUALITY_ATTEMPTS=1..5`, never the TOR thresholds. The low-priority weekly systemd crawl intentionally excludes Lighthouse because CPU scheduling and the external Cloudflare hop produced false lab failures; use this gate interactively against the release candidate or local production origin, and use protected RUM for field performance.
* The LCP-stabilization release defers `web-vitals` registration until browser idle time and skips below-fold layout/paint with explicit contrast surfaces. Recovery snapshot: `/var/www/eprscan-release-backups/pre-lcp-stabilization-20260902-1347`.
* The first English draft-preview release can be recovered from `/var/www/eprscan-release-backups/pre-draft-preview-20260902-1448`.
* The native article presentation polish can be recovered from `/var/www/eprscan-release-backups/pre-article-style-polish-20260902-1528`. Its release verification includes desktop/mobile visual capture plus Lighthouse Accessibility for the private preview; `noindex` is intentional and is not an SEO failure.
* The contextual-crosslink presentation release can be recovered from `/var/www/eprscan-release-backups/pre-crosslink-presentation-20260902-1550`. Verify the count of rendered `.article-crosslink` blocks against the draft's declared internal targets and require HTTP 200 from every target before acceptance.
* Localized unpublished draft support can be recovered from `/var/www/eprscan-release-backups/pre-draft-localizations-20260902`. The validator accepts only `de`, `fr` and `es` draft variants with a title and safe HTML; the English preview stays private and noindex.
* EPR content batching may temporarily stop `eprscan-blog-core-content.path` to prevent one production build per draft write. After the atomic batch write, run `eprscan-blog-core-content.service` once, confirm success, then restore the path unit. The unit must finish active/waiting and every private preview must return HTTP 200 before handoff.
* EPR batch database recovery points are `/var/www/blog.yas.ooo/backups/blog_core-pre-eprscan-batch-20260902.sqlite3` and `/var/www/blog.yas.ooo/backups/blog_core-pre-eprscan-localization-batch-20260902.sqlite3`.

## Independent Karp and Veronika native targets (2026-09-12)

* Karp: code `/var/www/karp-preview`, content `/var/lib/karp-preview/data/blog-core`, generated artifacts `/var/lib/karp-preview/generated`, DB `karp_preview`, public artifact process `karp-preview-artifact` on port `3045`.
* Veronika: code `/var/www/veronika-preview`, content `/var/lib/veronika-preview/data/blog-core`, generated artifacts `/var/lib/veronika-preview/generated`, DB `veronika_preview`, public artifact process `veronika-preview-artifact` on port `3055`.
* Recovery snapshots for the renderer integration are under `/var/backups/karp-preview/blog-core-native-20260912-165629`, `/var/backups/veronika-preview/blog-core-native-20260912-165629`, and the timestamped `pre-native-sites` Blog Core application/database files on the production host.
