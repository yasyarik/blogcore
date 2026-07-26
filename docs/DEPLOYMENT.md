# DEPLOYMENT.md

## Runtime

* 2026-07-26 contextual SEO-action release: `georivo-blog.service` renders one intent-specific, localized Georivo product step inside every informational detail page. Stylesheet revision: `20260726n`. Rollback target: `/var/backups/georivo-blogcore/20260726-contextual-seo-actions`.
* 2026-07-26 compact Pricing-card release: `georivo-blog.service` removes the overlapping/repeated hero checkout action and the side-by-side free-preview column. Pricing now uses one concise Georivo Solo card in normal flow with one checkout CTA. Stylesheet revision: `20260726l`. Rollback: `/var/backups/georivo-blogcore/20260726-pricing-card-compact`.
* 2026-07-26 CTA/pricing release: `georivo-blog.service` localizes informational and subscription actions, exposes the €49 Georivo Solo plan above Pricing SEO content, and keeps the real auth-to-Stripe checkout path. Guide title wrapping and mobile Pricing first paint were corrected in stylesheet revision `20260726k`. Rollback: `/var/backups/georivo-blogcore/20260726-cta-pricing`.
* 2026-07-26 content-template release: `georivo-blog.service` owns separate Blog and Guides templates. Verify `/ru/blog/`, `/ru/guides/`, and one `/ru/guides/<slug>/` route after deployment, and confirm the legacy `/georivo-hero.png` generic background is absent from the renderer stylesheet. Rollback: `/var/backups/georivo-blogcore/20260726-guide-template-split`.
* 2026-07-26 shared-chrome release: `georivo-blog.service` localizes the current Georivo header/footer server-side across five languages and consumes the compact three-column footer layout from the current Sites product stylesheet. Rollback: `/var/backups/georivo-blogcore/20260726-shared-footer`.
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

Root money pages are created and published from Blog Core content jobs. Do not
restore or run the retired `seed_money_pages.py` manual publisher. A root
canonical requires a factory `seo_money_page` job with
`canonicalRootPage=true`, `targetPath=/{slug}`, a generated-content contract,
validated localizations, and an explicit Publish action.

The Georivo renderer converts that validated HTML into its commercial section
layout at request time. Release checks must include
`audit_money_pages.py --origin https://georivo.com` plus desktop and 390 px
browser checks. The 2026-07-25 pre-redesign renderer backup is stored at
`/var/backups/georivo-blogcore/20260725-money-layout`.

The 2026-07-25 content-density/style refinement is deployed from
`deploy/georivo/app.py` and `deploy/georivo/georivo-blog.css`. Its immediate
pre-change rollback copy is stored at
`/var/backups/georivo-blogcore/20260725-money-style-polish`. Release QA must
also include a tablet-width check because the hero typography changes below
900 px.

The 2026-07-26 money-page visual-fill release adds hero-contained TOC,
supporting section imagery, and photo recommendation cards. Its immediate
pre-change rollback copy is stored at
`/var/backups/georivo-blogcore/20260726-money-visual-fill`. The tracked audit
file must also be copied to
`/var/www/blog.yas.ooo/deploy/georivo/audit_money_pages.py`, which is the
scheduled production-audit source.

The 2026-07-26 unique-alternating-media correction has rollback files at
`/var/backups/georivo-blogcore/20260726-money-unique-alternate`. Its release
audit verifies that every primary section has media, odd/even sections alternate
right/left, and no generated supporting-image URL repeats.

The 2026-07-26 global visual-identity release is Blog Core commit `f0fb285`.
It partitions all non-money-page media across the three root money pages,
including recommendation cards, and uses permanent Georivo-owned Coverage and
Pricing hero assets from Sites version 77. Rollback files are in
`/var/backups/georivo-blogcore/20260726-money-global-visuals`. The strict audit
must report zero main-image overlap between the three slugs in every language.

## Environment

* `PORT`: default `3299`.
* `ADMIN_HOSTS`: default `blog.yas.ooo,127.0.0.1,localhost`.
* `CNAME_TARGET`: default `blog.yas.ooo`.
* `HOSTED_BLOG_IPS`: default `72.61.1.109`.
* `GEMINI_API_KEY` or `GOOGLE_API_KEY`: enables Gemini article generation and automatic site topic-profile inference.
* `GEMINI_TEXT_MODEL`, `GEMINI_MODEL_TEXT`, or `GEMINI_MODEL`: optional text-model override.
* `GSC_SERVICE_ACCOUNT_FILE`: optional path override for deploy scripts that submit sitemaps through Google Search Console.
* `GSC_INSPECTION_URLS`: optional comma-separated canonical URL override for the daily Search Console URL Inspection set.

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
