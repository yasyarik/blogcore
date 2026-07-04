# CHANGELOG_AI.md

This file is updated by Codex after every task.

## 2026-07-04 — Collapse planned jobs by canonical task

### Summary

* Updated the planned publications UI so legacy per-language rows are grouped into one canonical task per topic/path.
* Corrected AIREP24 site language configuration from EN/DE/ES/FR back to EN only.
* Planned rows now show active generation languages from site settings and show old extra language rows as legacy variants.

### Files changed

* `app.py` — added planned-job grouping by canonical group/base path and language-aware primary-row selection.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that generation tasks should be canonical and language expansion should come from site settings.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Preserve old per-language rows in SQLite for traceability, but do not show them as separate generation tasks.
* Use `sites.languages` as the active language set for new generation. For AIREP24, active languages are now `["en"]`.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Updated live AIREP24 site `id=9` `sites.languages` to `["en"]`.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` planned block now renders 14 planned rows instead of 56.
* Verified the database still preserves 56 queued legacy rows grouped into 14 canonical groups.
* Verified planned rows show `Generates: EN` and legacy variant chips.

### Risks / TODO

* The generation endpoint still operates on a single primary `content_jobs` row. Full multi-language generation should be implemented as a canonical parent task with language child outputs in a future schema/publisher pass.

## 2026-07-04 — Point imported-site open action to live blogs

### Summary

* Changed the primary top/dashboard open action for imported sites from generated Blog Core previews to the live source-site blog URL.
* Imported local-path sites now show `Open live blog` and link to `https://domain/blog/`.

### Files changed

* `app.py` — added primary site link selection based on imported inventory and live blog URL generation.
* `docs/PROJECT_MEMORY.md` — recorded that imported blogs should open the live source-site blog, not generated previews.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Generated previews remain available as a technical Build preview flow, but they are not the main open action for existing imported blogs.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` contains `Open live blog` and `https://airep24.com/blog/`, and no longer contains `/previews/9/blog/`.
* Verified the dashboard contains live blog links for imported sites.

### Risks / TODO

* The generated preview files still exist under `/previews/...`; they are not deleted because they may still be useful for technical checks.

## 2026-07-04 — Add content type filter chips

### Summary

* Added content-type filters to the Content inventory toolbar.
* Operators can now switch between `All`, `Blog`, `SEO money`, `Home`, and `Other` while keeping the selected language.
* Pagination and the content jobs API now preserve and expose the selected content type.

### Files changed

* `app.py` — added `content_job_page_type`, server-side `content_type` filtering, filter chips, pagination query preservation, API response fields, and compact toolbar styling.
* `docs/PROJECT_MEMORY.md` — recorded the durable Content inventory filtering rule.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Type filters are server-side, matching the existing language filter behavior.
* Available content types are calculated after the language filter so the chips reflect what exists in the selected language.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified API counts for AIREP24 EN: `All=31`, `Blog=20`, `SEO money=10`, `Home=1`.
* Verified live `/sites/9?content_lang=en&content_type=seo_money_page#content` contains type filter chips and preserves `content_type=seo_money_page` in language links.

### Risks / TODO

* Content inventory still includes both imported live records and queued content records according to the current underlying list behavior; planned jobs also remain visible in the Distribution planned block.

## 2026-07-04 — Fully migrate AIREP24 legacy factory jobs

### Summary

* Migrated all legacy `jobs` from `/var/www/content-factory-airep24/factory.sqlite` into Blog Core site `id=9`.
* Preserved old factory job IDs, content type, page kind, locale/language, target path, canonical group, legacy status, and social status columns in Blog Core metadata/columns.
* Expanded the `Planned publications` dashboard block so it shows all planned jobs instead of only the first 12, with content type, language, and target path metadata.

### Files changed

* `app.py` — raised planned publication display limit to 200 and added compact language/type/target-path metadata to planned rows.
* `docs/PROJECT_MEMORY.md` — replaced the partial AIREP24 import note with the complete migration state.
* `docs/SEO_MEMORY.md` — recorded AIREP24 SEO money-page migration behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Old AIREP24 `NEW` jobs were migrated as Blog Core `QUEUED` planned jobs, not as imported live pages.
* Old AIREP24 `PUBLISHED` jobs were migrated as Blog Core `IMPORTED` inventory records.
* The old `content-factory-airep24` process/database was left in place; this task copied state into Blog Core without deleting the source factory.

### Checks run

* Created live DB backup `/var/www/blog.yas.ooo/data/blog_core.sqlite3.before-airep24-full-migration-20260704144135.bak`.
* Migrated 64 legacy records: 56 `QUEUED` and 8 `IMPORTED`.
* Verified Blog Core site `id=9` now has 80 `content_jobs`: 24 imported inventory records and 56 planned jobs.
* Verified planned jobs consist of 20 blog jobs and 36 SEO money-page jobs across EN/DE/ES/FR.
* Verified 64 records have `sources_json.migratedFrom=content-factory-airep24`.
* Ran `python3 -m py_compile app.py` locally and on the VPS.
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Verified `http://127.0.0.1:3299/health`.
* Verified live `/sites/9` HTML contains 56 planned rows, planned metadata, SEO money-page badges, and migrated target paths.

### Risks / TODO

* Final publish-back from Blog Core into `/var/www/airep24.com` for these queued jobs still depends on the broader local static publisher/parity work.
* The legacy `content-factory-airep24` process remains online as a source/rollback reference until an explicit cutover/removal decision is made.

## 2026-07-04 — Import airep24.com from local VPS webroot

### Summary

* Connected `airep24.com` to Blog Core as site `id=9`.
* Confirmed the active nginx config serves `airep24.com` from `/var/www/airep24.com`.
* Scanned the live homepage design; Gemini inferred the AIREP24 topic profile for Discovery settings.
* Imported existing AIREP24 blog pages directly from the local VPS webroot.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `airep24.com`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `airep24.com` is managed as a local-path site because the authoritative static site files are present on the same VPS at `/var/www/airep24.com`.
* The `/blog/` hub was imported as metadata but remains hidden from the Content inventory; the visible inventory contains the 15 article pages.

### Checks run

* Verified `airep24.com` was not already present in the Blog Core database.
* Checked nginx configs and confirmed the active domain root is `/var/www/airep24.com`.
* Verified `/var/www/airep24.com` contains 61 HTML files, including 16 under `/blog/`.
* Verified `https://airep24.com/sitemap.xml` exposes 16 `/blog/` URLs.
* Created site `id=9` with `access_type=local_path`, `root_path=/var/www/airep24.com`, and language EN.
* Ran `POST /api/sites/9/scan`; Gemini returned `source=gemini` topic profile data.
* Local Blog Core discovery returned `source=local_webroot`, 16 candidates, 0 warnings, 0 duplicates.
* Imported site `id=9` from local webroot: imported 16, skipped 0, errors 0.
* Verified imported counts: EN 16, all `pageType=blog`; 1 is the `/blog/` hub metadata record and 15 are visible article records.
* Verified all 16 imported records have `sources_json.webrootPath` under `/var/www/airep24.com` and `importMethod=direct_webroot`.
* Ran `POST /api/sites/9/bootstrap-preview`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/9#content` contains `AIREP24`, `/var/www/airep24.com`, `Content inventory`, language switching, `LIVE / IMPORTED`, and `Social drafts`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* Publishing new generated AIREP24 articles back into `/var/www/airep24.com` is still future publish-back work; this task imported and connected the existing blog inventory/control-plane records.

## 2026-07-04 — Clean VPS temporary files and caches

### Summary

* Inspected VPS disk usage and large backup/temp/cache files.
* Removed safe rebuildable caches and temporary files.
* Left active Chromium/Playwright runtime/cache paths untouched because processes were using them.
* Left `.git/objects/pack` files untouched because they are required repository data, not disposable backups.

### Files changed

* `docs/CHANGELOG_AI.md` — logged this VPS maintenance task.

### Decisions

* Cleaned only recoverable cache/temp/log data and one obsolete dev SQLite backup.
* Did not delete working databases, webroot HTML, source trees, `node_modules`, or Git pack files.

### Checks run

* Checked `df -hT`; root filesystem went from 79G used / 18G free / 83% to 76G used / 21G free / 79%.
* Removed `.next`/Turbopack caches for `build.yas.ooo`, `my-ugc-studio-saas`, `my-ugc-studio-saas-staging`, and `revaltix`.
* Removed root tool caches: pip, Prisma, TypeScript, cloud-code, node-gyp, and Jedi.
* Removed `/tmp/shopify-new`, `/tmp/tsx-0`, `/tmp/inspectroute-backend.tgz`, `/tmp/yas-agent-vps.tgz`, and old `.tmp` files under `/root/.gemini`.
* Truncated `/var/www/my-ugc-studio-saas/logs/access.log`.
* Ran `apt-get clean`.
* Ran `journalctl --vacuum-size=100M`.
* Removed `/var/www/highpurebreed/backups/dev.sqlite.before-calendly-ai-20260622182214.bak`.
* Verified `http://127.0.0.1:3299/health` still returns OK.

### Risks / TODO

* `/tmp/snap-private-tmp/snap.chromium` and `/root/.cache/ms-playwright` still use about 2GB combined, but active Chromium/Playwright processes were using them, so they were intentionally not removed.
* Large `.git/objects/pack` files remain the biggest large-file category; do not delete them manually.

## 2026-07-03 — Add channel-specific social draft adaptation

### Summary

* Added per-channel social draft generation for content jobs.
* Added strict character-limit validation before saving social drafts.
* Preserved article language for social drafts using `sources_json.language` with site-language fallback.
* Added a `Social drafts` action to content cards and updated social status icons to show drafted channel state.

### Files changed

* `app.py` — expanded `social_posts` schema, added social channel limits, language-aware post generation, validation/shortening, API route, content-card action, and JS handler.
* `docs/PROJECT_MEMORY.md` — recorded durable social draft rules and channel limits.
* `docs/INTEGRATIONS.md` — documented the social draft endpoint, storage contract, language behavior, and limits.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Store adapted social texts in `social_posts` before real publishing, one row per `job_id + channel` draft attempt.
* Use conservative strict limits: LinkedIn 3000, Telegram 4096, X/Twitter 280, Tumblr 4096.
* Do not rely on social platforms truncating overlong text; saved drafts must validate with `char_count <= max_chars`.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Ran `python3 -m py_compile app.py` on the VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Generated EN social drafts for LaycanMatch site `id=8`, job `38eae646b39daefef960f375`: LinkedIn 1626/3000, Telegram 1224/4096, X/Twitter 254/280, Tumblr 1064/4096.
* Verified saved `social_posts` rows have `status=DRAFT`, `language=en`, `char_count <= max_chars`, and matching `content_jobs` channel statuses set to `drafted`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/8#content` contains `Social drafts` actions and drafted channel icons.
* Generated a RU X/Twitter social draft for SoloCruz site `id=7`, job `6dc8145c44dcf8247dbf62e8`; result was `language=ru`, 261/280 characters, and Russian text.

### Risks / TODO

* Real provider publish calls are still pending; this task prepares validated social drafts but does not post them to LinkedIn, Telegram, X/Twitter, or Tumblr yet.
* Social draft generation currently calls Gemini once per channel; this can be optimized later into a single multi-channel generation call.

## 2026-07-03 — Import laycanmatch.com from local VPS webroot

### Summary

* Connected `laycanmatch.com` to Blog Core as site `id=8`.
* Confirmed the active nginx config serves `laycanmatch.com` from `/var/www/laycanmatch.com`.
* Scanned the live homepage design; Gemini inferred the LaycanMatch topic profile for Discovery settings.
* Imported existing LaycanMatch blog pages directly from the local VPS webroot.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `laycanmatch.com`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `laycanmatch.com` is managed as a local-path site because the authoritative static site files are present on the same VPS at `/var/www/laycanmatch.com`.
* The `/blog/` hub was imported as metadata but remains hidden from the Content inventory; the visible inventory contains the five article pages.

### Checks run

* Verified `laycanmatch.com` was not already present in the Blog Core database.
* Checked nginx configs and confirmed the active domain root is `/var/www/laycanmatch.com`.
* Verified `/var/www/laycanmatch.com` contains 44 HTML files, including 6 under `/blog/`.
* Verified `https://laycanmatch.com/sitemap.xml` exposes 6 `/blog/` URLs.
* Created site `id=8` with `access_type=local_path`, `root_path=/var/www/laycanmatch.com`, and language EN.
* Ran `POST /api/sites/8/scan`; Gemini returned `source=gemini` topic profile data.
* Local Blog Core discovery returned `source=local_webroot`, 6 candidates, 0 warnings, 0 duplicates.
* Imported site `id=8` from local webroot: imported 6, skipped 0, errors 0.
* Verified imported counts: EN 6, all `pageType=blog`.
* Verified all 6 imported records have `sources_json.webrootPath` under `/var/www/laycanmatch.com` and `importMethod=direct_webroot`.
* Ran `POST /api/sites/8/bootstrap-preview`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/8#content` contains `LaycanMatch`, `/var/www/laycanmatch.com`, `Content inventory`, language switching, and `LIVE / IMPORTED`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* Publishing new generated LaycanMatch articles back into `/var/www/laycanmatch.com` is still future publish-back work; this task imported and connected the existing blog inventory/control-plane records.

## 2026-07-03 — Import solocruz.com from local VPS webroot

### Summary

* Connected `solocruz.com` to Blog Core as site `id=7`.
* Confirmed the active nginx config serves `solocruz.com` from `/var/www/solocruz.com`.
* Scanned the live homepage design; Gemini inferred the SoloCruz topic profile for Discovery settings.
* Imported existing multilingual SoloCruz blog pages directly from the local VPS webroot.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `solocruz.com`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `solocruz.com` is managed as a local-path site because the authoritative static site files are present on the same VPS at `/var/www/solocruz.com`.
* The import kept existing live URLs as source-site authoritative records; Blog Core acts as inventory/control plane for the existing blog rather than changing public pages.

### Checks run

* Verified `solocruz.com` was not already present in the Blog Core database.
* Checked nginx configs and confirmed the active `000-solocruz.com.conf` root is `/var/www/solocruz.com`; the Hestia `/home/mysites/.../public_html` path has no blog HTML.
* Verified `https://solocruz.com/sitemap-blog.xml` exposes 75 blog URLs, 15 per EN/RU/ES/DE/FR.
* Created site `id=7` with `access_type=local_path`, `root_path=/var/www/solocruz.com`, and languages EN/RU/ES/DE/FR.
* Ran `POST /api/sites/7/scan`; Gemini returned `source=gemini` topic profile data.
* Local Blog Core discovery returned `source=local_webroot`, 75 candidates, 0 warnings, 0 duplicates.
* Imported site `id=7` from local webroot: imported 75, skipped 0, errors 0.
* Verified imported counts: EN 15, RU 15, ES 15, DE 15, FR 15; all are `pageType=blog`.
* Verified all 75 imported records have `sources_json.webrootPath` under `/var/www/solocruz.com` and `importMethod=direct_webroot`.
* Ran `POST /api/sites/7/bootstrap-preview`.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/7#content` contains `SoloCruz`, `/var/www/solocruz.com`, `Content inventory`, language switching, and `LIVE / IMPORTED`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* Publishing new generated SoloCruz articles back into `/var/www/solocruz.com` is still future publish-back work; this task imported and connected the existing blog inventory/control-plane records.

## 2026-07-03 — Reimport myugc.studio from local VPS webroot

### Summary

* Corrected the `myugc.studio` import source from public sitemap to the actual local webroot on the VPS.
* Found that active nginx serves `myugc.studio` from `/var/www/landing`; `/var/www/my-ugc-studio` is not the public static blog root.
* Updated Blog Core site `id=6` to `root_path=/var/www/landing` and `access_type=local_path`.
* Cleared the prior site `id=6` imported inventory and reimported from local files.

### Files changed

* `docs/PROJECT_MEMORY.md` — marked the earlier public-sitemap import note as replaced and recorded the actual local webroot import state.
* `docs/CHANGELOG_AI.md` — logged this correction.

### Decisions

* For `myugc.studio`, `/var/www/landing` is the authoritative local source for current public blog HTML and sitemap files.
* The earlier public-sitemap import was replaced because the VPS already has the static public blog files locally.

### Checks run

* Read active `/etc/nginx/conf.d/myugc.studio.conf`; confirmed `root /var/www/landing`.
* Verified `/var/www/landing` contains local blog HTML files and sitemap files.
* Local Blog Core discovery returned `source=local_webroot`, 442 unique candidates, 0 warnings.
* Reimported site `id=6` from local webroot: imported 442, skipped 0, errors 0.
* Verified site `id=6` now has `root_path=/var/www/landing` and `access_type=local_path`.
* Verified every imported `content_jobs` row for site `id=6` has `sources_json.webrootPath` under `/var/www/landing`.
* Verified language counts: EN 88 stored records, DE 89, ES 89, FR 89, RU 87.
* Verified `/api/sites/6/content-jobs?language=en` returns 87 visible EN records after hiding the `/blog/` hub.
* Verified live dashboard HTML contains `/var/www/landing`, `LIVE / IMPORTED`, `My UGC Studio`, and language switching.

### Risks / TODO

* Publishing new generated articles back into `/var/www/landing` is still future publish-back work; this task corrected the import/control-plane inventory source.

## 2026-07-03 — Import myugc.studio blog into Blog Core

### Summary

* Connected `myugc.studio` to Blog Core as site `id=6`.
* Scanned the live homepage design and let Gemini infer the site's discovery direction/category profile.
* Imported existing `myugc.studio` blog URLs non-destructively from public sitemaps.
* Left the live `myugc.studio` site untouched; imported records point back to the original published URLs.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the durable production import state for `myugc.studio`.
* `docs/CHANGELOG_AI.md` — logged this import task.

### Decisions

* `myugc.studio` was imported as `public_sitemap` without `root_path` because `/var/www/my-ugc-studio` has no static `/blog/*.html` files. Using a local root would make Blog Core's current import scanner stop at an empty webroot result instead of reading public sitemaps.

### Checks run

* Verified `myugc.studio` was not already present in Blog Core.
* Checked VPS roots and nginx config for `myugc.studio`.
* Verified public sitemap sources include multilingual blog URLs.
* Created/updated site `id=6` in the live Blog Core SQLite database.
* Ran `POST /api/sites/6/scan`; Gemini returned a topic profile for My UGC Studio.
* Ran `POST /api/sites/6/import-blog/scan`; found 343 public-fetch blog URLs.
* Ran `POST /api/sites/6/import-blog/import`; imported 343, skipped 0, errors 0.
* Verified imported counts by language: EN 43 stored records, DE 75, ES 75, FR 75, RU 75.
* Verified `/api/sites/6/content-jobs?language=en` returns 42 visible EN article records after hiding the `/blog/` hub.
* Verified live dashboard HTML for `https://blog.yas.ooo/sites/6#content` contains `My UGC Studio`, `Content inventory`, language switching, and `LIVE / IMPORTED`.
* Ran `POST /api/sites/6/bootstrap-preview`.
* Checked `http://127.0.0.1:3299/health`.

### Risks / TODO

* The import is stored in the live SQLite database, which is intentionally not committed to Git.
* Publishing new generated My UGC Studio articles back into the original site locations is still future publish-back work; imported records are currently dashboard inventory/control-plane records.

## 2026-07-03 — Add social credential setup and connection tests

### Summary

* Added a `Social channel credentials` block to the Setup tab.
* Added per-site credential forms for LinkedIn, Telegram, X/Twitter, and Tumblr.
* Added `Save credentials` and `Test connect` actions for each provider.
* Updated Distribution channel cards to point to Setup and show `Configure in Setup`, `Ready to test`, or `Connected` based on saved/tested status.

### Files changed

* `app.py` — added social provider credential config, per-site save/test API routes, provider API probes, Setup UI, JS handlers, and status styling.
* `docs/PROJECT_MEMORY.md` — recorded the durable Setup-vs-Distribution social channel rule and secret-handling rule.
* `docs/INTEGRATIONS.md` — documented social credential storage and connection test behavior.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Setup is where keys/tokens are entered and tested. Distribution only controls autopublish selection for configured/connected channels.
* Saved secrets are kept in SQLite `social_connections.credentials_json` and are not rendered back into the dashboard.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified live `https://blog.yas.ooo/sites/5#setup` contains social credential forms and JS handlers.
* Verified live HTML does not contain raw env secret names such as `GEMINI_API_KEY`.
* Smoke-tested Telegram save endpoint with empty payload and Telegram test endpoint; missing credentials return a controlled `400` with `Missing required credentials`.

### Risks / TODO

* Real social publishing routes still need to use these stored per-site credentials.
* OAuth authorization flows for providers that need browser-based authorization are still not implemented; current Setup supports entering issued tokens/keys and testing them.

## 2026-07-03 — Auto-infer Discovery settings from scanned site

### Summary

* Added Gemini-based site topic-profile inference during `Scan design`.
* `Discovery direction` and `Category hint` are now auto-filled from scanned homepage metadata/nav/footer when empty.
* Added a deterministic fallback so scans still succeed if Gemini is unavailable.
* Updated `run.sh` to source `/var/www/blog.yas.ooo/.env` before Gunicorn, and configured the live VPS `.env` with existing Gemini/Google key/model env vars without committing secrets.
* Ran a live scan for `yas.wine` and updated site `id=5` with Gemini-inferred Discovery settings.

### Files changed

* `app.py` — added site topic-profile prompt/inference/fallback logic and connected it to the scan route; updated Distribution field hints.
* `run.sh` — loads `.env` before starting Gunicorn.
* `docs/PROJECT_MEMORY.md` — recorded Gemini topic-profile inference and `.env` runtime behavior.
* `docs/DEPLOYMENT.md` — documented `.env` loading and Gemini env vars without secrets.
* `docs/INTEGRATIONS.md` — documented the topic-profile inference contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Gemini should infer a site's initial editorial direction and category hints from the site scan; the UI fields remain editable overrides.
* Normal scans preserve manual overrides by writing inferred values only when the fields are empty.
* Missing Gemini configuration is degraded behavior; fallback values are allowed so site scanning is not blocked.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` and `run.sh` to `/var/www/blog.yas.ooo/`.
* Created `/var/www/blog.yas.ooo/.env` on the VPS from existing Gemini/Google env names without exposing values; `.env` remains untracked.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Ran `POST http://127.0.0.1:3299/api/sites/5/scan`; verified Gemini returned `source=gemini`.
* Verified `/api/sites/5/factory-settings` now returns Gemini-inferred `direction` and `category_hint` for YAS Wine.

### Risks / TODO

* Topic inference depends on Gemini env vars being present in the runtime `.env`.
* Existing manually edited Discovery fields are intentionally not overwritten by future scans.

## 2026-07-03 — Clarify social connect state and planned publications placement

### Summary

* Replaced active-looking social `Connect` buttons with non-clickable `OAuth setup needed` indicators until per-site OAuth/connect routes are implemented.
* Moved `Planned publications` to the bottom of Distribution below the social channel settings.
* Changed the no-planned-publications state from a large empty panel to a compact row.

### Files changed

* `app.py` — updated Distribution rendering, removed the placeholder connect toast function, and added compact planned-publication/connection-state CSS.
* `docs/PROJECT_MEMORY.md` — recorded durable UI rules for disabled social connect state and bottom placement of planned publications.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Non-implemented OAuth/connect actions should be shown as setup state, not as buttons that appear to do something.
* Planned publication tasks belong at the bottom of Distribution under social channels, not above the channel controls.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified live HTML for `https://blog.yas.ooo/sites/5#distribution`: no `connectSocialChannel`, no connect `onclick`, `OAuth setup needed` indicators present, `Planned publications` appears after `Channels`, compact `planned-empty` is present.

### Risks / TODO

* Per-site OAuth/connect routes for LinkedIn, Telegram, X/Twitter, and Tumblr still need real implementation before accounts can be connected.
* Planned publications still show only current working content job statuses, not a calendar/time-based publishing schedule.

## 2026-07-03 — Move planned publications into Distribution

### Summary

* Moved `Planned publications` out of the Content tab.
* Placed planned publication tasks under Distribution, directly below autopublish scheduler settings.
* Kept Content focused on imported/live inventory and import actions.

### Files changed

* `app.py` — moved planned publication rendering into `render_distribution_settings()` and removed the Content-tab planned section.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that planned/future publication tasks belong under Distribution scheduling.
* `docs/CHANGELOG_AI.md` — logged this placement correction.

### Decisions

* Planned tasks are part of publishing/scheduling workflow, so they belong with Distribution rather than Content inventory.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/sites/5#distribution`: `Planned publications` appears in Distribution, not in Content, and no `__PLANNED_PUBLICATIONS__` placeholder remains.

### Risks / TODO

* Planned publications are still status-based jobs, not a true scheduled calendar with publish timestamps.

## 2026-07-03 — Align multilingual content sorting and show planned publications

### Summary

* Fixed Content inventory sorting so language tabs keep the same article/topic order across EN/RU/ES/DE/FR.
* Added a separate `Planned publications` section for non-imported Blog Core work items.
* Planned publications now show `QUEUED`, `GENERATING`, `DRAFT`, and `ERROR` content jobs separately from imported live pages.

### Files changed

* `app.py` — added normalized base-path sort keys, planned content query/rendering, and a Content tab section for planned publications.
* `docs/PROJECT_MEMORY.md` — recorded stable cross-language sorting and planned-publication visibility rules.
* `docs/CHANGELOG_AI.md` — logged this inventory/scheduling UI fix.

### Decisions

* Imported multilingual content should sort by normalized source path, not by import timestamp or database id.
* Planned publications are currently content jobs in working statuses; a full scheduled calendar remains a future layer.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified first five normalized paths match across EN/RU/ES/DE/FR on `/api/sites/5/content-jobs`.
* Verified `https://blog.yas.ooo/sites/5#content` contains `Planned publications` and no leftover `__PLANNED_PUBLICATIONS__` placeholder.

### Risks / TODO

* `Planned publications` is not yet a time-based schedule/calendar because `content_jobs` does not have a scheduled publish timestamp.

## 2026-07-03 — Unify distribution channel controls

### Summary

* Removed duplicated social channel sections in Distribution.
* Replaced separate `Publish channels`, include-link checkboxes, and connection-status cards with one unified card per provider.
* Each channel card now shows connection status, a visible `Connect` placeholder, `Use for autopublish`, and `Include article link`.

### Files changed

* `app.py` — rewrote `render_distribution_settings()` channel UI, added unified channel CSS, and added a `connectSocialChannel()` placeholder toast.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule to keep social provider controls unified.
* `docs/CHANGELOG_AI.md` — logged this Distribution UI fix.

### Decisions

* Until per-site OAuth/connect routes are implemented, `Connect` should be visible but honest that the route is not wired yet.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/sites/5#distribution` no longer contains `Publish channels` or `Channel connection status`, and contains unified channel cards with `Use for autopublish`, `Include article link`, and Connect controls.

### Risks / TODO

* Per-site OAuth/connect routes are still not implemented; Connect currently shows a placeholder toast.

## 2026-07-03 — Filter trade-promo Discovery signals

### Summary

* Added filtering for promotional/trade campaign signals such as grants, retailer campaigns, `Wine Month`, and money-based promo headlines.
* Confirmed `Indies to receive £250 for Bordeaux Wine Month` is classified as promotion/trade-specific and filtered out.

### Files changed

* `app.py` — added promo/trade signal terms to `is_global_topic_signal()`.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that trade-promo/campaign items are not global discovery trends.
* `docs/CHANGELOG_AI.md` — logged this filtering refinement.

### Decisions

* Discovery should not show retailer/trade promotions as global content trends.

### Checks run

* `python3 -m py_compile app.py`
* Local classifier check returned `(False, 'promotion/trade-specific')` for `Indies to receive £250 for Bordeaux Wine Month`.
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/api/sites/5/topic-signals?range=month` no longer contains `Indies to receive`.

### Risks / TODO

* Filtering remains heuristic; add source/domain quality scoring if weak celebrity or brand-news items still appear.

## 2026-07-03 — Filter Discovery to broad global signals

### Summary

* Changed topic discovery to use a broader global/consumer/industry signal query.
* Added filtering for city-specific, festival/event, ticket, local-opening, and local guide signals before showing Google/Reddit items.
* Updated Discovery copy to clarify that local events and one-off news are filtered out.
* Article idea jobs now instruct generation to turn signals into generalizable articles, not city/event/festival pieces.

### Files changed

* `app.py` — added global signal query construction, local/event signal filters, warnings for filtered signals, Discovery UI copy, and article idea angle guidance.
* `docs/PROJECT_MEMORY.md` — recorded the durable global-signal rule for Discovery.
* `docs/CHANGELOG_AI.md` — logged this filtering change.

### Decisions

* Discovery should surface broad topic/consumer/industry trends, not local event feeds.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/api/sites/5/topic-signals?range=month` uses query `wine food pairing global trends consumer industry`, filters local/event Google and Reddit items, and no longer returns the earlier `Castro Wine Fest` items.

### Risks / TODO

* Filtering is heuristic. Some weak celebrity or brand-news items can still pass if they are not local/event-specific; future scoring can add a stronger editorial-quality layer.

## 2026-07-03 — Add language switching and simplify content pagination

### Summary

* Changed Content inventory to default to a concrete language instead of mixing all imported languages.
* Added language chips for available content languages (`EN`, `RU`, `ES`, `DE`, `FR`).
* Simplified Content inventory pagination to one centered bottom nav with numeric links and arrow icons only.

### Files changed

* `app.py` — added content job language detection/filtering, language switcher rendering, API language metadata, and simplified bottom-only pagination.
* `docs/PROJECT_MEMORY.md` — recorded durable rules for language-separated inventory and compact bottom-only pagination.
* `docs/CHANGELOG_AI.md` — logged this UI/data filtering task.

### Decisions

* Multilingual imported content must be browsed per language by default; `All` is not shown in the Content inventory UI.
* Pagination should be unobtrusive and only at the bottom of the content list.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `/api/sites/5/content-jobs?page=1&per_page=24` returns `language=en`, `total=166`, and sample rows all have `sources_json.language=en`.
* Verified `/api/sites/5/content-jobs?page=1&per_page=24&language=ru` returns `language=ru`, `total=160`, and sample rows all have `sources_json.language=ru`.
* Verified `https://blog.yas.ooo/sites/5#content` has language chips, no `Page 1 of`/`Showing` text, and exactly one bottom pagination nav: `1 2 3 ›`.

### Risks / TODO

* The API still supports `language=all` if explicitly requested, but the dashboard UI intentionally does not expose an all-languages mixed view.

## 2026-07-03 — Compact imported content actions and type badges

### Summary

* Replaced the visible `Open live page` text button with a compact external-link icon in Content inventory cards.
* Styled `LIVE / IMPORTED` as a green status badge.
* Added compact content type badges for imported records, including `Blog` and `SEO money page`.

### Files changed

* `app.py` — added live-page icon rendering, content type badge rendering, and CSS for imported status/type/action indicators.
* `docs/PROJECT_MEMORY.md` — recorded durable UI rules for compact content card actions and type badges.
* `docs/CHANGELOG_AI.md` — logged this UI refinement.

### Decisions

* Imported content cards should show ownership/status/type at a glance without large action buttons.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Fetched `https://blog.yas.ooo/sites/5#content` and verified a production card action row renders `SEO money page`, `LIVE / IMPORTED`, and an external-link `↗` icon.

### Risks / TODO

* Browser runtime checks timed out during this task, so verification used live HTML fetch and server health checks.

## 2026-07-03 — Compact social status indicators in content cards

### Summary

* Replaced large per-channel social status pills in Content inventory cards with compact icon indicators.
* Muted unpublished/not queued channels visually and kept tooltips/ARIA labels with the exact channel status.
* Deployed the dashboard UI fix to live Blog Core.

### Files changed

* `app.py` — added social status icon rendering and CSS for muted/queued/published/failed states.
* `docs/PROJECT_MEMORY.md` — recorded the durable UI rule for compact social status indicators.
* `docs/CHANGELOG_AI.md` — logged this UI fix.

### Decisions

* Social publishing status in content cards should be a compact visual indicator, not a row of large text buttons.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Browser check of `https://blog.yas.ooo/sites/5#content`: first content card has four `.social-icon` elements at 30x30, old `linkedin: not queued` text is absent, and muted icons have opacity `0.32`.

### Risks / TODO

* The current icons are lightweight text glyphs (`in`, `tg`, `X`, `t`) because Blog Core has no frontend icon package. They can later be replaced with SVG brand icons if the dashboard adds an icon asset strategy.

## 2026-07-03 — Fix public YAS Wine blog pagination

### Summary

* Corrected the target from Blog Core dashboard pagination to the public source-site page `https://yas.wine/blog/`.
* Replaced the public blog's `More guides` load-more behavior with visible pagination controls: `Previous`, numbered pages, and `Next`.
* Updated the public page counter to show `Page X of Y · Showing A-B of N guides`.

### Files changed

* `/var/www/yaswine/blog/index.html` — live source-site file edited directly on the VPS; backup created at `/var/www/yaswine/blog/index.html.bak-pagination-20260703-1248`.
* `docs/PROJECT_MEMORY.md` — recorded the durable distinction between Blog Core dashboard pagination and source-site public blog pagination.
* `docs/CHANGELOG_AI.md` — logged this public-site pagination fix.

### Decisions

* Public `yas.wine/blog/` pagination belongs to the source site's webroot, not to Blog Core dashboard rendering.
* Keep 12 cards per page and use `?page=N` URLs for direct navigation.

### Checks run

* Browser check of `https://yas.wine/blog/`: 61 total cards, 12 visible cards, `More guides` hidden, pager visible with `Previous 1 2 3 4 5 6 Next`, and text `Page 1 of 6 · Showing 1-12 of 61 guides`.
* Browser check of `https://yas.wine/blog/?page=2`: active page `2`, 12 visible cards, and text `Page 2 of 6 · Showing 13-24 of 61 guides`.

### Risks / TODO

* The public blog pagination is client-side over the existing static 61-card page. SEO/server-rendered paginated archive pages are still a separate future improvement if needed.

## 2026-07-03 — Make content pagination explicit

### Summary

* Changed Content inventory pagination from bare page numbers to an explicit `Page X of Y` block.
* Renamed numeric links to `Page 1`, `Page 2`, etc. so the controls read as pagination instead of stray numbers.
* Deployed the UI clarification to live Blog Core.

### Files changed

* `app.py` — updated `render_content_pagination()` labels and CSS for clearer visible pagination.
* `docs/CHANGELOG_AI.md` — logged this pagination clarity fix.

### Decisions

* Pagination controls must be visually explicit on large imported inventories; bare numbers are too easy to miss.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Browser reload of `https://blog.yas.ooo/sites/5#content` confirmed visible text: `Page 1 of 34`, `Page 1`, `Page 2`, `Page 3`, `Next`.

### Risks / TODO

* Filters by content type/status/language are still needed for large imports, but pagination is now visibly present.

## 2026-07-03 — Hide imported hub pages and add content pagination

### Summary

* Hid imported section listing/hub pages such as `/blog/`, language blog indexes, `/wine-countries/`, and `/wine-regions/` from the Content inventory work list.
* Added server-side pagination metadata and UI controls for the Content inventory.
* Updated the Content inventory copy to explain that listing pages are kept as import metadata, not shown as article/task cards.

### Files changed

* `app.py` — added imported hub detection, paginated `get_content_jobs()`, pagination rendering, API pagination fields, and Content inventory explanatory copy.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that imported hub/listing pages are metadata and Content inventory must stay paginated.
* `docs/CHANGELOG_AI.md` — logged this UI/data-list fix.

### Decisions

* Do not delete imported hub/listing pages from the database. Hide them from the work list so Blog Core preserves source-site structure without confusing those pages with articles.
* Keep `/api/sites/<id>/content-jobs` backward compatible by still returning `jobs`, while adding `page`, `per_page`, `total`, and `total_pages`.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified `https://blog.yas.ooo/api/sites/5/content-jobs?page=1&per_page=24` returns `total=806`, `total_pages=34`, `jobs=24`, and no first-page job with `published_url=https://yas.wine/blog/`.
* Verified `https://blog.yas.ooo/sites/5#content` contains `Content inventory`, pagination UI, and the hub-page explanatory note, and no card title `Wine Blog: Pairing Guides, Wine Tips and Buying Advice | YAS Wine`.

### Risks / TODO

* Content inventory still needs filters by status/type/language for very large imports.
* Imported hub pages are hidden from this UI list only; they remain in the database for source-site metadata.

## 2026-07-03 — Clarify imported content versus publication tasks

### Summary

* Renamed the `Article production queue` section to `Content inventory`.
* Changed `IMPORTED` cards to show `LIVE / IMPORTED` and `Open live page`.
* Removed `Generate draft` actions from imported records so already-published source pages are not presented as unpublished tasks.
* Updated explanatory copy: imported pages are already live on the source site; queued items are future work.

### Files changed

* `app.py` — updated `render_content_jobs()` labels/actions and the Content tab heading/copy.
* `docs/PROJECT_MEMORY.md` — recorded the durable UI distinction between imported live pages and queued generation tasks.
* `docs/CHANGELOG_AI.md` — logged this UI clarification task.

### Decisions

* `IMPORTED` means an existing live source-site page imported into Blog Core's control-plane inventory. It is not a publication task.
* Generation buttons belong only on new/queued Blog Core tasks, not on imported live pages.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Fetched `https://blog.yas.ooo/sites/5#content` and verified `Content inventory`, `LIVE / IMPORTED`, and `Open live page` are present while `Article production queue` and `Generate draft` are absent for imported rows.
* Browser DOM check confirmed the same state and no console errors/warnings.

### Risks / TODO

* The `Content` tab still needs filters/pagination to separate imported live pages, queued tasks, drafts, and published-by-Blog-Core records at scale.

## 2026-07-03 — Split site manage page into tabs

### Summary

* Reorganized the site manage page into clear tabs: `Content`, `Discovery`, `Distribution`, `Activity`, and `Setup`.
* Moved import controls and article production queue into `Content`.
* Moved Google/Reddit topic signals into `Discovery`.
* Kept autopublish/social channel settings in `Distribution`.
* Moved `Factory jobs` into `Activity` and site/webroot/CNAME/design controls into `Setup`.
* Deployed the tabbed UI to live Blog Core and validated desktop/mobile rendering in the in-app browser.

### Files changed

* `app.py` — added tab navigation, tab panels, tab switching JS, and tab styles in `MANAGE_SITE_HTML`.
* `docs/PROJECT_MEMORY.md` — documented the durable tab organization rule.
* `docs/CHANGELOG_AI.md` — logged this UI organization task.

### Decisions

* The manage page should keep operational concerns separate: content work, discovery, distribution, activity logs, and technical setup should not share one long mixed page.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Browser QA on `https://blog.yas.ooo/sites/5`: page identity, tab visibility, tab clicks, console errors/warnings, desktop screenshot, and mobile viewport screenshot.

### Risks / TODO

* The content queue still returns only the latest 24 records; full filtering/pagination remains needed for large imports such as 821 `yas.wine` records.

## 2026-07-03 — Summarize factory job messages in UI

### Summary

* Fixed the `Factory jobs` panel rendering huge raw JSON payloads from import jobs.
* Added compact job-message summaries for import and article-idea jobs.
* Added CSS clamping/overflow protection for job messages so a long payload cannot break the page layout.
* Deployed the fix to live Blog Core and verified `/sites/5` no longer contains the repeated `already imported` JSON dump.

### Files changed

* `app.py` — added `summarize_job_message()` and changed `render_jobs()` to display summaries instead of raw `publish_jobs.message`.
* `docs/PROJECT_MEMORY.md` — recorded the durable UI rule to summarize job messages.
* `docs/CHANGELOG_AI.md` — logged this UI fix.

### Decisions

* `publish_jobs.message` can keep structured JSON for internal/debug use, but the dashboard must present compact human-readable summaries.

### Checks run

* `python3 -m py_compile app.py`
* Deployed `app.py` to `/var/www/blog.yas.ooo/app.py`.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Fetched `https://blog.yas.ooo/sites/5` and confirmed the page shows `imported 0; skipped 821; errors 0` instead of raw JSON.

### Risks / TODO

* The factory jobs panel still needs richer pagination/filtering, but it no longer breaks the page.

## 2026-07-03 — Replace partial YAS Wine import with full webroot import

### Summary

* Corrected the earlier partial `yas.wine` import approach. The 61 URL count was only the public English `/blog/` index, not the real site inventory.
* Inspected `/var/www/yaswine` directly over SSH and found 828 candidate HTML files, 821 distinct canonical URLs, 433 blog files, and 395 `wine-countries`/`wine-regions` SEO money page files.
* Backed up the live Blog Core SQLite database and imported the missing 760 records directly from `/var/www/yaswine`.
* Updated the existing 61 records with direct `webrootPath`, page type, language, and source-site-authoritative metadata.
* Updated and deployed `app.py` so future local-site imports use `root_path` filesystem discovery, include multilingual blog pages and SEO money pages, and use public fetch only as fallback.

### Files changed

* `app.py` — added local webroot import discovery/extraction, multilingual blog and SEO money page import prefixes, recursive sitemap-index fallback, path-safe import slugs, and higher import batch limit.
* `docs/PROJECT_MEMORY.md` — replaced the incomplete 61-URL state note with the full 821-record production state.
* `docs/INTEGRATIONS.md` — documented direct webroot import behavior.
* `docs/SEO_MEMORY.md` — recorded that imported SEO money pages are part of local-site inventory.
* `docs/CHANGELOG_AI.md` — logged this correction.

### Decisions

* For VPS-local imported sites, direct webroot inventory is authoritative. Public crawling is only a fallback for external sites.
* SEO money pages under `wine-countries` and `wine-regions` are imported content for Blog Core control-plane purposes, not ignored non-blog pages.

### Checks run

* Backed up `/var/www/blog.yas.ooo/data/blog_core.sqlite3`.
* Imported `yas.wine` from `/var/www/yaswine`: 821 distinct imported records total.
* Verified DB counts: `IMPORTED=821`, `Imported Blog=426`, `Imported SEO Money Page=395`.
* Verified language metadata: `en=169`, `ru=163`, `es=163`, `de=163`, `fr=163`.
* `python3 -m py_compile app.py` locally and on VPS.
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Verified live scan endpoint returns `source=local_webroot`, `articles=821`, `duplicates=7`.
* Verified repeat API import returns `0 imported`, `821 skipped`, `0 errors`.

### Risks / TODO

* UI currently lists only the latest 24 content jobs via `/api/sites/<id>/content-jobs`; filtering/pagination is needed to manage all 821 imported records comfortably.
* Publishing generated updates back into exact source files/URLs still needs the publish-back-in-place pipeline.

## 2026-07-03 — Import YAS Wine into live Blog Core

### Summary

* Imported the existing `yas.wine` blog into live Blog Core site `id=5`.
* The production scan found 61 English article URLs from `https://yas.wine/blog/`.
* The import created 61 `content_jobs` with `status=IMPORTED`, preserved original `published_url` values, and reported 0 errors.
* A repeat import check returned 0 imported, 61 skipped as `already imported`, confirming duplicate protection.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded the live `yas.wine` import state and scripted API User-Agent pitfall.
* `docs/CHANGELOG_AI.md` — logged this production import verification task.

### Decisions

* Keep `yas.wine` original `/blog/...` URLs authoritative after import; imported jobs are control-plane records for now.

### Checks run

* `GET https://blog.yas.ooo/health`
* `GET https://blog.yas.ooo/api/sites`
* `POST https://blog.yas.ooo/api/sites/5/import-blog/scan`
* `POST https://blog.yas.ooo/api/sites/5/import-blog/import`
* `GET https://blog.yas.ooo/api/sites/5/content-jobs`
* `GET https://blog.yas.ooo/api/sites/5/content-jobs/f0c496a5a5fc26cc67077613`
* `curl -I -L https://yas.wine/blog/wine-region-napa-valley-united-states/`

### Risks / TODO

* Current import covered English URLs discoverable from `/blog/`; multilingual URLs in `sitemap_index.xml` still need recursive sitemap-index discovery.
* Publishing generated tasks back into the original `yas.wine` locations is not implemented yet.

## 2026-07-03 — Clarify imported-blog ownership model

### Summary

* Clarified that the "Blog Core as control plane, not public mirror" rule applies to imported existing blogs only.
* Documented that imported blogs should keep publishing into the same original site locations and URL structure.
* Preserved the separate rule that blogs created by Blog Core from scratch can be fully owned, hosted, and published by Blog Core.

### Files changed

* `docs/PROJECT_MEMORY.md` — added imported-vs-created ownership distinction and decision log entry.
* `docs/SEO_MEMORY.md` — clarified canonical behavior for imported blogs versus Blog Core-created blogs.
* `docs/INTEGRATIONS.md` — clarified import publishing target and current hosted mirror/preview caveat.
* `docs/CHANGELOG_AI.md` — logged this clarification task.

### Decisions

* Imported existing blogs are managed in place by default: original URLs stay authoritative, and future generated tasks should publish back into those same locations.
* Blog Core-created blogs can be native Blog Core publications with Blog Core as the source of truth.

### Checks run

* Read existing project memory, SEO memory, integrations memory, and changelog before editing.

### Risks / TODO

* Implement publish-back-in-place for imported blogs; current code still has hosted mirror rendering and incomplete local/static export parity.

## 2026-07-03 — Analyze YAS Wine import coexistence

### Summary

* Checked how imported articles coexist with the source site's existing blog.
* Inspected `yas.wine` public blog, robots, sitemap index, article canonical metadata, and import/rendering code.
* Confirmed that import is non-destructive and stores source canonical URLs, but hosted rendering does not yet emit canonical tags from that stored source URL.
* Confirmed that current discovery finds 61 English `yas.wine/blog/` article URLs from the blog index, while `sitemap-blog.xml` and `/blog/sitemap.xml` return 404.

### Files changed

* `docs/PROJECT_MEMORY.md` — recorded duplicate-content/canonical migration rule and `sitemap_index.xml` import pitfall.
* `docs/SEO_MEMORY.md` — documented source canonical/noindex recommendation during coexistence and the missing hosted canonical output.
* `docs/INTEGRATIONS.md` — documented current `yas.wine` import discovery behavior and sitemap-index limitation.
* `docs/CHANGELOG_AI.md` — logged this analysis task.

### Decisions

* Treat the source blog URL as authoritative until an explicit cutover is implemented.
* Do not expose a public indexed Blog Core mirror of imported content without canonical/noindex/redirect strategy.

### Checks run

* Read project memory and import/render code.
* `curl -I -L https://yas.wine/blog/`
* Fetched `https://yas.wine/robots.txt`, `https://yas.wine/sitemap.xml`, `https://yas.wine/sitemap_index.xml`, language sitemaps, and a sample article canonical.
* Counted 61 candidate English article URLs from `https://yas.wine/blog/`.

### Risks / TODO

* Add recursive sitemap-index discovery for multilingual imports.
* Add hosted canonical/noindex behavior before exposing imported mirrors to search engines.

## 2026-07-03 — Refresh self-updating project memory after local clone

### Summary

* Verified the separate local clone at `/Users/yasyas/Library/Mobile Documents/com~apple~CloudDocs/проекты/blogcore`.
* Read existing memory, README, runtime files, nginx template, `.gitignore`, and key `app.py` routes/schema before editing.
* Tightened future-agent memory rules and refreshed durable project/deployment/SEO notes from confirmed repository state.
* Marked the older SEO sitemap limitation as replaced for hosted CNAME blogs while preserving the remaining local static export gap.

### Files changed

* `AGENTS.md` — clarified mandatory final memory-status reporting and Git remote expectations for VPS vs local clones.
* `docs/PROJECT_MEMORY.md` — refreshed durable product, architecture, SEO, deployment, pitfalls, and decisions after local clone setup.
* `docs/SEO_MEMORY.md` — updated hosted sitemap/content-job behavior and marked the stale dynamic-sitemap gap as replaced.
* `docs/DEPLOYMENT.md` — recorded local clone path and Git access notes without secrets.
* `docs/CHANGELOG_AI.md` — logged this memory refresh task.

### Decisions

* Future Codex sessions must treat repository memory as the durable source of truth and still verify relevant code before changes.
* Local HTTPS Git access through GitHub CLI is acceptable when SSH publickey auth is unavailable locally; VPS SSH remote remains valid server context.

### Checks run

* `python3 -m py_compile app.py`
* `git status --short --branch`
* Read `AGENTS.md`, `README.md`, `.gitignore`, `requirements.txt`, `run.sh`, `deploy/nginx-blog.yas.ooo.conf`, docs memory files, and relevant `app.py` schema/routes.

### Risks / TODO

* Keep memory concise; do not duplicate all code details.
* Final article publishing/export, social OAuth/publishing, autopublish runner, GSC/sitemap submission, and production custom-domain SSL remain incomplete parity items.

## 2026-07-01 — Set up self-updating project memory

### Summary

* Added repository-level project memory and future-agent instructions.
* Documented confirmed product overview, architecture, business rules, integrations, SEO/content behavior, deployment notes, known pitfalls, and prior decisions.
* Added the rule that Codex must read memory before non-trivial tasks and update changelog/memory after completed tasks.

### Files changed

* `AGENTS.md` — added required memory workflow, what to store/avoid, and repository rules.
* `docs/PROJECT_MEMORY.md` — created durable project memory with product, architecture, deployment, integration, SEO, pitfalls, decisions, and do-not-repeat notes.
* `docs/CHANGELOG_AI.md` — created AI changelog and logged this memory setup task.
* `docs/BUSINESS_CONTEXT.md` — documented business/product context.
* `docs/DEPLOYMENT.md` — documented runtime, PM2, nginx, environment, and deployment checks.
* `docs/INTEGRATIONS.md` — documented scanner, CNAME, DNS, RSS, and SQLite integration contracts.
* `docs/SEO_MEMORY.md` — documented SEO/content behavior and current limitations.

### Decisions

* Memory files live inside the repository and must be maintained as part of future tasks.
* Sensitive values, raw logs, generated databases, previews, and secrets must not be stored in memory.

### Checks run

* Read existing `README.md`, `requirements.txt`, `run.sh`, `.gitignore`, `app.py`, nginx configs, PM2 process details, Git history, and SQLite schema.
* Confirmed `python3 -m py_compile app.py` still passes before creating memory files.

### Risks / TODO

* Keep memory concise and durable; avoid turning it into a duplicate of the full codebase.
* Future agents must update this file after every completed task.

## 2026-07-01 — Clean up topic discovery signal quality

### Summary

* Removed Reddit/Google source failures from selectable signal cards.
* Increased topic discovery capacity to 20 usable signals per source.
* Added relevance scoring, deduplication, and Reddit discussion filtering so article ideas are based on top/relevant signals instead of random or error items.
* Updated the manage-page UI to show source warnings as notes and display signal counts.

### Files changed

* `app.py` — changed Google and Reddit signal fetchers to return `(signals, warnings)`, added scoring/filtering, updated `/topic-signals` API payload, and updated signal UI rendering.
* `docs/PROJECT_MEMORY.md` — recorded the durable rule that source errors must be warnings, not cards.
* `docs/INTEGRATIONS.md` — documented the topic discovery contract and limitations.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Do not pad the signal grid with low-relevance or failed-source items just to increase card count.
* Reddit RSS 429 is an expected degraded state and should not block Google signals.

### Checks run

* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/api/sites/5/topic-signals` for `week`, `month`, `3m`, and `6m`; confirmed no disabled/error cards and no zero-score returned signals.

### Risks / TODO

* Reddit RSS can still rate-limit; a more reliable Reddit integration may require API credentials or caching/backoff.
* Current Google source is Google News RSS, not official Google Trends.

## 2026-07-01 — Add YAS Wine factory parity backbone

### Summary

* Audited `/var/www/content-factory-yaswine` for article jobs, social publishing, autopublish, topic discovery, and generation flow.
* Added a parity map documenting which YAS Wine factory capabilities must exist in universal Blog Core.
* Added per-site Blog Core schema for article production jobs, job logs, social connections, social posts, autopublish settings/runs, and topic discovery settings/runs.
* Added manage-page Production Queue and Distribution/autopublish settings UI.
* Changed selected topic signals to create real `content_jobs`, not only legacy `publish_jobs`.
* Added a universal Gemini draft-generation contract for `content_jobs` that uses connected site context instead of wine-only rules.

### Files changed

* `app.py` — added factory parity tables, per-site settings helpers/endpoints, content job creation/list/detail/generate routes, manage-page production/distribution panels, and universal article draft generation.
* `docs/FACTORY_PARITY.md` — added the source-to-target parity map from YAS Wine factory to Blog Core.
* `docs/PROJECT_MEMORY.md` — recorded durable parity decision.
* `docs/INTEGRATIONS.md` — documented current backbone and pending provider/publish parity work.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Provider credentials and publishing settings must be scoped by `site_id`.
* Do not copy the YAS Wine prompt literally into Blog Core; use the same quality contract with site-specific context.
* Keep old `publish_jobs` as legacy/service jobs while new article production uses `content_jobs`.

### Checks run

* `python3 -m py_compile app.py`
* Ran `init_db()` against the live SQLite database to create new tables.
* Restarted PM2 process `blog-yas-core`.
* Checked `/health`.
* Smoke-tested `/api/sites/5/factory-settings`, `/api/sites/5/article-ideas`, and `/api/sites/5/content-jobs/<job_id>`; removed smoke job afterward.

### Risks / TODO

* Full parity is not finished yet: real social publishing routes, OAuth callbacks, autopublish runner, and final publish/localization/sitemap/GSC behavior still need to be ported.
* Real Gemini generation route exists but was not smoke-run to avoid spending model calls on a test topic.

## 2026-07-01 — Tighten Reddit topic relevance

### Summary

* Fixed Reddit topic discovery passing unrelated discussions when they matched only generic words from the site topic seed.
* Added a stricter Reddit relevance gate requiring a strong site-topic anchor plus contextual title match.
* Verified that broad YAS Wine false positives such as generic food/SNAP/mountain supply posts are rejected.

### Files changed

* `app.py` — added Reddit weak-term filtering, shared term matching, and `reddit_signal_is_relevant()` for stronger discussion filtering.
* `docs/PROJECT_MEMORY.md` — recorded the durable Reddit relevance rule.
* `docs/INTEGRATIONS.md` — documented the stricter Reddit signal contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Prefer returning zero Reddit cards with a warning over showing random or weakly related discussions.

### Checks run

* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Checked `/api/sites/5/topic-signals?range=month`; Reddit false positives were removed and the API returned a no-relevant-Reddit warning.

### Risks / TODO

* Reddit RSS can still rate-limit or return sparse results. A better long-term solution is a credentialed Reddit API integration with subreddit/topic expansion and caching.

## 2026-07-01 — Add existing blog import flow

### Summary

* Added a per-site existing blog import workflow to Blog Core.
* Added scan/import endpoints that discover current `/blog/` article URLs from sitemaps and blog index links.
* Imported articles are stored as `content_jobs` with `status=IMPORTED`, preserving original URL/canonical metadata and captured HTML without changing live files.
* Hosted Blog Core rendering now lists imported/generated jobs, includes them in hosted sitemap, and serves `/blog/{slug}/` from saved job HTML.
* Added dashboard UI inside each site page to scan existing blog URLs, review them, and import selected articles.

### Files changed

* `app.py` — added article metadata parser, existing blog discovery/import helpers, import API routes, site import UI/JS, and dynamic hosted rendering for imported/generated jobs.
* `docs/PROJECT_MEMORY.md` — recorded the migration/import rule.
* `docs/INTEGRATIONS.md` — documented the existing blog import contract.
* `docs/CHANGELOG_AI.md` — logged this task.

### Decisions

* Existing blog migration starts as a non-destructive import into Blog Core, not as an overwrite of live `/blog` files.
* Imported articles use `content_jobs.status=IMPORTED` so they are visible to the same production system without pretending they were generated by Blog Core.

### Checks run

* `python3 -m py_compile app.py`
* Restarted PM2 process `blog-yas-core`.
* Checked `http://127.0.0.1:3299/health`.
* Smoke-tested `/api/sites/5/import-blog/scan`; found 61 `yas.wine` article URLs.
* Smoke-imported one `yas.wine` article, verified dynamic render by slug, then removed the smoke job/log from SQLite.

### Risks / TODO

* Import currently stores referenced media URLs and article HTML but does not copy media into Blog Core storage yet. A later migration step should add optional media mirroring before switching a live site.
* Hosted rendering supports imported jobs, but local static `/blog` install still writes only the sample shell until final publishing/export parity is completed.
