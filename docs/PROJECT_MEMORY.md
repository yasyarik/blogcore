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
  - Manage a site's factory settings, discover topic signals, select trends/discussions, queue article idea jobs, generate draft article jobs, and import existing `/blog/` articles as preserved Blog Core content jobs.

## 2. Current architecture

* Frontend: Server-rendered HTML/CSS/JS strings inside `app.py`; no frontend build pipeline.
* Backend: Python Flask app in `app.py` served by Gunicorn.
* Database: SQLite at `data/blog_core.sqlite3`; `data/` is ignored and must not be committed.
* Hosting: VPS path `/var/www/blog.yas.ooo`; PM2 process `blog-yas-core` runs `run.sh`.
* Scheduled page publishing: PM2 process `blog-yas-core-scheduler` runs `run-scheduler.sh` once per minute. It advances only explicitly scheduled `content_jobs` through the native factory lifecycle and does not distribute social posts.
* Auth: No application-level dashboard auth is implemented in the MVP. The private YAS Source Scanner draft-ingestion endpoint uses a shared secret header and must never expose or log its value.
* Payments: None.
* Main external services:
  - Public site HTML/CSS fetched via `urllib.request` for design scanning.
  - Popular topic discovery uses Google autocomplete/search suggestions as a non-news search-demand signal source, plus Reddit top discussions.
  - Reddit search RSS is used for discussion signals; it may rate-limit.
  - DNS resolution uses Python `socket.getaddrinfo` for CNAME/custom-domain status checks.
  - Gemini text generation is used for draft generation and for automatic site topic-profile inference when `GEMINI_API_KEY` or `GOOGLE_API_KEY` is configured.
  - Draft generation is represented by the content job generation contract in `app.py`; provider credentials/secrets must not be committed or documented in raw form.
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
* Generate/regenerate, Preview, and Publish are separate operator actions. Generating a draft must not automatically publish it. `DRAFT` tasks need an explicit Publish action. For imported/source-authoritative jobs, Publish delegates to the original source factory rather than editing source-site files directly from Blog Core.
* Finished Source Scanner Studio drafts can be inserted into the target site's task queue only through the authenticated source-scanner endpoint. They arrive as `DRAFT` tasks with their authored HTML, source attribution, FAQ and scanner-hosted media; Blog Core must not regenerate or auto-publish them. Re-sending an unpublished scanner draft updates the same task. A published task cannot be replaced through this integration. Native YAS draft-store preparation remains specific to `yas.ooo`; other sites are queued without assuming a publication adapter.


* Blog Core must support arbitrary external sites, not just sites hosted on this VPS.
* External sites should normally use hosted CNAME blog routing instead of requiring SSH/SFTP/Git/CMS access.
* Local install is only for sites whose filesystem root is available on the same VPS and configured in `root_path`.
* Deleting a connected site from the dashboard must remove only Blog Core records and preview cache. It must not delete installed `/blog` files from the target site root.
* Factory settings are per site: content context, topic strategy, languages, cadence, CNAME settings, and jobs belong to the site.
* `Discovery direction` and `Category hint` should be auto-inferred from the scanned site with Gemini during `Scan design`. They remain editable overrides, but should not be empty/manual-first for newly scanned sites. If Gemini is unavailable, use a deterministic metadata fallback and do not block scanning.
* The manage page should allow switching between connected sites without returning to the dashboard.
* Factory parity with the old YAS Wine factory must include article jobs, logs, generation modes, social channels, autopublish settings, topic discovery settings, and publish status per site.
* Social publishing/OAuth must be scoped per site, not globally.
* Setup must include per-site social channel credential configuration for LinkedIn, Telegram, X/Twitter, Tumblr, Pinterest, Instagram, and Threads, with Save credentials and Test connect actions. Distribution should only select which configured/connected channels are used for autopublish.
* Social publishing drafts must be adapted per channel and per article language before publishing. Blog Core stores one `social_posts` draft per `job_id + channel`, validates exact character counts before saving, and must not rely on social platforms truncating overlong text.
* Pinterest drafts are not plain text posts. Blog Core must generate a native Pinterest pin creative spec from the article: title, description/caption, overlay text, alt text, vertical 2:3 image prompt, recommended size, and optional destination URL. The pin spec is stored in `social_posts.content_json`.
* Instagram drafts are native carousel creatives, not plain text posts and not SVG/mock previews. Blog Core generates one shared carousel caption plus real 4:5 JPEG slide assets through Gemini Image, stores slide metadata in `social_posts.content_json.instagramCarousel`, and serves generated files from ignored `data/social_assets/...`. Instagram has one caption for the whole carousel; per-slide text is visual overlay/review metadata only.
* Instagram captions have a hard maximum of 2200 characters, but Blog Core should target a much shorter default caption around 700 characters for generated carousel posts. The caption should be a compact hook/context/CTA with no more than three hashtags, because slide content carries the details.
* Instagram publishing must go through the project's third-party intermediary publishing server, not direct Instagram Graph API calls from Blog Core.
* Threads is a separate social channel from X/Twitter and Instagram. Threads drafts must feel native to Threads: short, conversational, question-led or opinion-led, not promotional ad copy. They must stay within 500 UTF-8 bytes, use at most one hashtag, and should generate one separate Threads-specific image: simple, natural, non-advertising, no overlay text, no logo, no UI screenshot, not reused from Instagram carousel creative. Blog Core should validate bytes, not only Python character count, because emoji/non-ASCII text can exceed platform limits sooner.
* Social publishing drafts must not be offered or generated unless at least one social channel is both selected in Distribution and configured/connected in Setup. There must be no fallback that silently generates drafts for every provider when channels are missing.
* Technical settings should stay compact on the site factory page; main workflow should focus on topic discovery and jobs.
* Existing imported blogs and Blog Core-created blogs have different ownership models. For imported existing blogs, Blog Core should act as the control plane/dashboard and publish new/updated tasks back into the same original site locations and URL structure. It should not default to becoming a second public copy of that blog. For blogs created by Blog Core from scratch, Blog Core can be the full source of truth and public hosting/publishing layer.
* For imported sites that have legacy/source factory jobs (`sources_json.migratedFrom` and `oldFactoryJobId`), Blog Core must not use its generic article generator. It must delegate generation to the source site's factory so validation, length rules, internal-link rules, image generation, SEO money-page contracts, and publishing requirements remain site-specific.
* Legacy/source factory generation must be recoverable after Blog Core restarts. The content-job status API should re-check the source factory for `GENERATING` legacy jobs, sync `READY`/`PUBLISHED` drafts back into Blog Core, surface legacy `ERROR`, and mark stale long-running legacy jobs instead of leaving the dashboard stuck forever.
* For imported existing blogs, primary dashboard open actions should point to the live source-site blog URL, not to generated Blog Core previews. Generated previews are only useful for new/from-scratch Blog Core blogs or technical design checks.
* Dashboard site cards for imported live sites must not show new-site setup actions such as `Scan design`, `Build preview`, or `Install /blog`. Imported site cards should focus on `Manage`, live-site status, `Open live blog`, and safe dashboard removal.
* The site manage page is organized by tabs: `Content` for import and article production queue, `Discovery` for topic signals, `Distribution` for autopublish/social settings, `Activity` for system/factory job logs, and `Setup` for webroot/CNAME/design settings.
* In the `Content` tab, imported records must be presented as already-live source-site pages, not as publication tasks. Use labels such as `Content inventory`, `LIVE / IMPORTED`, and `Open live page`; reserve generation actions for `QUEUED`/new Blog Core tasks.
* In content cards, social publishing status must be compact icon indicators, not large text pills. Unpublished/not queued channels should be visually muted; published/sent channels should appear active.
* Content card actions should stay compact: use an external-link icon for the live URL action, render `LIVE / IMPORTED` as a green status, and show content type with small badges such as `Blog` or `SEO money page`.
* Content inventory must not mix languages by default. Use language switching chips (`EN`, `RU`, `ES`, `DE`, `FR`) and filter content jobs by language server-side.
* Content inventory must also support content-type switching chips so operators can filter the same list by `All`, `Blog`, `SEO money page`, `Home`, or `Other` while preserving the selected language and pagination state.
* Content inventory sorting must be stable across languages. Sort imported pages by normalized base URL/path with the language prefix removed, so switching `EN/RU/ES/DE/FR` keeps the same article/topic positions when translations exist.
* Content inventory pagination should appear only once at the bottom of the list, centered, using compact numeric links and arrow icons without `Page X of Y` wording.
* Planned/future Blog Core publications should be visible separately from imported live pages. Show `Planned publications` at the bottom of Distribution, below the social channel settings, for `QUEUED`, `GENERATING`, `DRAFT`, and `ERROR` content jobs; imported live pages stay in Content inventory. If there are no planned jobs, keep the empty state compact.
* Discovery must be a two-step workflow: operators select topic signals, generate article idea candidates, review/select specific ideas, then add selected ideas to Planned publications. Selecting signals alone must not immediately create planned jobs.
* Discovery article ideas must be checked for similarity against existing imported/published and already planned site content before they are shown and again before they are queued. Topics that are too similar to existing content should be filtered or rejected instead of creating duplicate/near-duplicate planned tasks.
* Discovery must distinguish raw audience/search-demand signals from final article ideas. Search autocomplete signals are not time-filtered; period controls apply only to Reddit discussion signals. The UI/API should show raw, filtered, kept, and source-specific warnings so users understand why the visible count changes.
* Discovery UI should not force operators to review and check every raw audience signal before generating ideas. Raw signals are selected automatically after deep analysis, hidden from the main workflow, and summarized with counts/status. The article idea generation button stays disabled until signal analysis finishes.
* Long-running Discovery idea generation must show visible in-page progress, not only a toast or static loading text. The UI should show an active loader, elapsed time, and current stage while the article-ideas request is running.
* Discovery article idea generation should return as many valid editorial/SEO ideas as actually survive checks, not an arbitrary product target such as 4, 12, or 16. The generator may run multiple Gemini passes until a pass adds no new valid ideas, while a technical safety cap only prevents runaway cost/latency. UI/API should show accepted/generated/rejected/pass counts.
* Discovery article ideas must be formed from Google Search Central 2026 generative-search principles: unique, valuable, non-commodity, people-first pages that fit the connected site's business, audience, expertise, existing content, and SEO opportunity. Raw search/Reddit signals are audience-interest inputs, not titles.
* For product/commercial sites, Discovery should prefer concrete audience problems, business impact, decision context, product-category value, adoption blockers, ROI/efficiency context, objections, and misconceptions. It must not default to generic SERP-clone formats such as numbered listicles, `best/top tools`, review/comparison roundups, buyer frameworks, or build/setup/configuration tutorials unless the site's own topic strategy explicitly allows those editorial formats.
* Discovery article idea validation must reject obsolete years earlier than the current year and reject title formats that do not match the site's editorial policy. Editorial-format permissions should come from the site's scanned/profile strategy and settings, not from already-generated content that may contain bad old patterns.
* Discovery article idea cards must not display raw dirty autocomplete strings such as `best ... 2025` as the visible source/query line. `target_query_cluster` and the displayed source line should be normalized SEO clusters without obsolete years or generic SERP modifiers.
* Discovery must deduplicate article ideas semantically within the same generation run, not only by exact title. Multiple signals pointing to the same core problem should become one strong idea, not several near-duplicate cards.
* Discovery article ideas should carry explicit editorial diversity fields such as `topic_axis` and `audience_problem`. Same-run dedupe should compare these axes so the final idea set covers distinct problems/outcomes/funnel moments rather than several versions of the same commercial angle.
* Planned generation work should be shown as one canonical task per topic/path, not as separate tasks per language. The task should generate the site's configured languages. Legacy per-language factory rows may be preserved in the database for traceability, but the dashboard should collapse them by canonical group/base path and show extra old languages only as legacy variants.
* Planned task groups should support bulk operations from the dashboard. Bulk generate runs selected canonical tasks one by one from the browser to avoid long single-request timeouts. Bulk delete removes selected planned groups from Blog Core records/logs/social drafts only; it must not delete live source-site files.
* Long-running generation must show persistent in-page progress, not only a toast. When a task reaches `DRAFT`, the dashboard must provide a `Preview draft` action that opens the generated HTML before publishing.
* Any task with `status=GENERATING` must render an animated in-card progress indicator and poll its content-job API until it becomes `DRAFT` or `ERROR`. This is especially important for legacy/source factory jobs where the initial generate request returns immediately while the source factory continues asynchronously.
* `DRAFT` planned/content tasks must also expose an explicit `Regenerate draft` action. Regeneration should overwrite the current draft/artifacts for the same task instead of requiring deletion and re-queueing.
* Article/page draft generation must show visible progress while the request is running. Single-job generation should update both the in-page planned-publications progress area and the toast with elapsed time/stage text.
* Article/page draft generation must not ask Gemini to return a large raw HTML fragment inside a JSON string. That pattern causes malformed JSON when HTML attributes, quotes, or long fragments are not escaped perfectly. Blog Core should request structured article fields through Gemini `responseSchema` and render the final HTML server-side.
* Replaced/deprecated 2026-07-09: The previous malformed-JSON repair pass should not be the primary correctness mechanism for article/page generation. Generic JSON repair may remain as a fallback for non-article helpers, but article/page drafts should be correct by construction through structured schema output.
* Structured article rendering must preserve the full article/page block contract: one page title rendered outside the body, non-duplicated meta description and lead, TOC from section headings, 3 body figures, useful table, ordered list, quote, and 5-7 FAQ items. Do not regress back to short body-only drafts.
* Generic Blog Core article/page drafts must pass server-side validation before becoming `DRAFT`: minimum useful length, enough sections, exactly 3 body image specs, FAQ, table, and ordered list. Invalid structured output should fail with a clear generation error instead of being saved as a ready draft.
* Generic Blog Core article/page drafts must generate real JPEG article assets through Gemini Image: one hero image for cards plus 3 body images. Generated files live in ignored `data/article_assets/...` and are served by Blog Core asset routes. Imported legacy factory jobs continue to use their source factory output instead.
* Gemini Image article assets must use supported aspect ratios only. For generic article hero/body images, use `16:9`; do not use unsupported ratios such as `16:10`.
* For local imported sites with `root_path`, `Preview draft` must render through the real source-site HTML template/assets from the webroot, not through the generic Blog Core preview shell. The preview should be noindexed and preserve source-site visual classes, header, footer, and assets while replacing only the draft content area.
* Local imported-site draft previews may inherit the source template's `<base href="https://source-site/">`. Blog Core preview-only links inside generated draft bodies must therefore be rewritten to absolute Blog Core URLs for `/sites/.../article-assets/...`, and TOC fragment links must point to the current preview URL plus `#anchor`.
* Local imported-site draft previews should preserve source-site post-article sections that follow the main article/content block, such as recommendations, related content, newsletter/signup, or update blocks. Do this with template-pattern extraction, not domain-specific hardcoding.
* Local imported-site draft previews should adapt generic Blog Core FAQ markup to the source template's FAQ pattern when recognizable, such as `faq-grid`/`faq-card`, instead of always showing raw generic `<details>` styling.
* Distribution channel settings should not duplicate the same providers across separate blocks. Each channel card should combine connection status, Connect action, autopublish enablement, and include-link setting in one place.
* Social channel status in Distribution should point users to Setup when credentials are missing, show `configured` after credentials are saved, and `connected` only after a successful test.
* Imported section listing/hub pages such as `/blog/`, language blog indexes, `/wine-countries/`, and `/wine-regions/` may be stored as import metadata, but they must be hidden from the Content inventory work list so they are not confused with articles or publish tasks.

## 4. Integrations

* Design scanner fetches the connected homepage URL and captures title, meta description, stylesheet URLs, inline `<style>`, body class, nav/header/footer, colors, and fonts.
* If source CSS includes native patterns `.section`, `.blog-card`, `.blog-carousel`, and `.container`, generated blog pages reuse native-looking markup.
* Hosted CNAME blog routing uses `Host` header lookup against `sites.custom_blog_domain` when `hosted_blog_enabled=1`.
* CNAME status check compares resolved custom domain IPs against `HOSTED_BLOG_IPS` or the resolved `CNAME_TARGET`.
* Topic discovery must not use news feeds as the default source of "trends". Use broad non-news search/topic-demand signals and Reddit top discussions, derived from the site's Discovery direction/category hint/topic profile.
* Reddit signal fetching uses `https://www.reddit.com/search.rss` with top sorting; rate limits are expected and must be handled gracefully without rendering error cards. Reddit matches must include a strong site-topic anchor and contextual match; do not surface broad matches based only on generic words like `food`, `product`, or `shop`.
* Discovery signals should be broad/global topic signals suitable for scalable articles. Filter out city-specific, festival/event, ticket, local-opening, trade-promo/campaign/grant/retailer, navigation/source-specific autocomplete tails such as `youtube`/`reddit`, and one-off news signals before showing them as selectable search/Reddit items.
* Discovery topic normalization must preserve short meaningful category terms such as `AI` and `UGC`, normalize phrases such as `user generated content` to `ugc` and `e-commerce` to `ecommerce`, and not discard category-defining terms just because they also appear in the brand/domain. Relevance matching should use whole words, not accidental substrings inside unrelated words.
* Discovery topic selection must be content-informed across the whole connected site, not derived from one heading or the first words of a category hint. Query candidates should use scanned profile/settings plus existing imported/planned content titles, descriptions, categories, slugs, and URLs. For multilingual imports, prefer English/canonical content when enough records exist so non-English fragments do not become query seeds.
* Discovery query candidates should prefer multiword editorial/product clusters over single generic tokens such as `ai`, `questions`, or `support`. Single tokens may be anchors, but not the main query when content clusters exist.
* Article ideas must be generated by the journalist/SEO prompt from selected audience signals and existing-site context. Do not copy autocomplete suggestions or Reddit titles directly as article titles; generated ideas need SEO intent/rationale and must be checked against already imported/published/planned content.
* The journalist/SEO prompt must first understand the site, then cluster audience signals into real needs, and only then produce article ideas with target query clusters, business relevance, unique site context, and duplicate-check rationale.
* Existing blog import scans sitemap and `/blog/` index sources for external sites. If a connected site has a local `root_path`, import must prefer direct webroot discovery and include multilingual `/blog/` pages plus SEO money pages under `wine-countries` and `wine-regions`.
* Social credentials are stored per site in SQLite `social_connections.credentials_json`; secrets must not be rendered back into the page, committed, or written to memory files.
* Social post adaptation uses `social_posts` for per-channel drafts. Current hard limits are LinkedIn 3000, Telegram 4096, X/Twitter 280, Tumblr 4096, and Pinterest description 500 characters. The generator uses the article language from `content_jobs.sources_json.language` when present, falls back to the site's first configured language, and rejects/squeezes output before saving if it would exceed the channel limit.
* Replaced/deprecated 2026-07-03: The earlier production state note saying `yas.wine` import found only 61 English `/blog/` URLs was an incomplete external-scan result, not a complete import.
* Current production state: On 2026-07-03, `yas.wine` site `id=5` was fully imported from local webroot `/var/www/yaswine`. Blog Core now has 821 distinct `content_jobs.status=IMPORTED`: 426 blog pages and 395 SEO money pages. All records have `published_url` on `https://yas.wine/...` and `sources_json.webrootPath` pointing to the source file.
* Replaced/deprecated 2026-07-03: The earlier `myugc.studio` import as `public_sitemap` with 343 records was based on checking the wrong local path (`/var/www/my-ugc-studio`). The public site is served by nginx from `/var/www/landing`, not `/var/www/my-ugc-studio`.
* Current production state: On 2026-07-03, `myugc.studio` site `id=6` was reconnected to Blog Core with `root_path=/var/www/landing` and `access_type=local_path`. Blog Core reimported 442 distinct existing blog URLs directly from the local VPS webroot with `sources_json.webrootPath` pointing to `/var/www/landing/...`: EN 88 stored records, DE 89, ES 89, FR 89, RU 87. The Content inventory hides hub pages such as `/blog/`, so EN shows 87 visible article records.
* Current production state: On 2026-07-03, `solocruz.com` site `id=7` was connected to Blog Core with `root_path=/var/www/solocruz.com` and `access_type=local_path`. Blog Core imported 75 existing blog URLs directly from the local VPS webroot with `sources_json.webrootPath` pointing to `/var/www/solocruz.com/...`: EN 15, RU 15, ES 15, DE 15, FR 15. Records are `status=IMPORTED`, `pageType=blog`, and keep `https://solocruz.com/...` as the source-site authoritative `published_url`.
* Current production state: On 2026-07-03, `laycanmatch.com` site `id=8` was connected to Blog Core with `root_path=/var/www/laycanmatch.com` and `access_type=local_path`. Blog Core imported 6 existing English blog URLs directly from the local VPS webroot with `sources_json.webrootPath` pointing to `/var/www/laycanmatch.com/...`: 5 article pages plus the `/blog/` hub metadata record. The Content inventory hides the hub, so 5 imported live article records are visible.
* Replaced/deprecated 2026-07-04: The initial `airep24.com` import moved only 16 English `/blog/` URLs from `/var/www/airep24.com`; that was not a complete factory migration.
* Current production state: On 2026-07-04, `airep24.com` site `id=9` was connected to Blog Core with `root_path=/var/www/airep24.com` and `access_type=local_path`, then fully migrated from `/var/www/content-factory-airep24/factory.sqlite`. Blog Core now has 80 AIREP24 `content_jobs`: 24 `IMPORTED` inventory records and 56 legacy `QUEUED` planned rows. The imported inventory contains the original 16 English blog/webroot records plus 8 legacy published factory records: 4 localized home pages and 4 localized `features/automated-knowledge-base` SEO money pages. The planned queue contains 20 blog rows and 36 SEO money-page rows with EN/DE/ES/FR legacy variants preserved in `sources_json`; the dashboard collapses those rows into 14 canonical planned tasks. AIREP24's active site language is EN only (`sites.languages=["en"]`), so new generation should target EN unless the site's language setting is changed.
* Current production state: On 2026-07-09, AIREP24 had duplicate comparison static paths for `airep24-vs-live-chat`: canonical `/comparisons/airep24-vs-live-chat/` and old `/compare/airep24-vs-live-chat/`. The old `/compare/...` page was manually synchronized with the canonical page in `/var/www/airep24.com/compare/airep24-vs-live-chat/index.html` and `/var/www/airep24-landing/compare/airep24-vs-live-chat/index.html` so it includes images, TOC, and FAQ.

## 5. SEO / content rules

* Hosted blogs serve `robots.txt` and `sitemap.xml` for the custom host.
* Hosted sitemap includes `/blog/` plus imported/generated public `content_jobs` when available; otherwise it falls back to the sample article.
* Local install writes `sitemap-blog.xml` and appends its URL to target site's `robots.txt` when possible.
* Generated sample blog/article content is placeholder-level and should not be treated as final editorial content. Existing blogs can be imported as `content_jobs.status=IMPORTED` while preserving original slugs, canonical/source URLs, metadata, and saved HTML.
* Legacy factory job migrations should preserve old factory IDs and target paths in `sources_json`; unfinished old `NEW` jobs should become Blog Core planned jobs (`QUEUED`) rather than imported live pages.
* Article ideas generated from trend/discussion signals are queued as jobs and should connect audience problems/questions to the site's offer, expertise, or editorial point of view.
* Article idea generation from Discovery signals should not create `content_jobs` directly. Only the selected ideas submitted through the queue step should create `content_jobs.status=QUEUED`.
* Final publishing parity is still incomplete: local static `/blog` install writes the sample shell, while hosted rendering can serve imported/generated content jobs.
* For imported blogs, the target behavior is not a public Blog Core mirror. Imported content should let Blog Core understand, display, manage, update, and create tasks for the existing blog while preserving the original live URL structure. The original site URL remains the canonical/authoritative destination unless an explicit cutover is requested.
* For imported local sites, distinguish Blog Core dashboard UI from the source site's public UI. Fixes requested against `https://yas.wine/blog/` usually require editing `/var/www/yaswine`, not only Blog Core's `/sites/<id>` dashboard.

## 6. Deployment

* Runtime command: `./run.sh`.
* `run.sh` loads `/var/www/blog.yas.ooo/.env` before starting Gunicorn; this is where live Gemini/Google API keys and model env vars should be configured. Do not commit `.env`.
* Gunicorn binds `127.0.0.1:3299` with 2 workers and 120 second timeout.
* PM2 process name: `blog-yas-core`.
* Public dashboard domain: `https://blog.yas.ooo`.
* Live nginx `blog.yas.ooo` vhost proxies to `http://127.0.0.1:3299`.
* Live default catchall nginx config proxies unknown HTTP/HTTPS Host traffic to Blog Core so CNAME domains can be routed by the Flask app.
* Current vhost/catchall configs reference self-signed certificate paths. Automated public SSL issuance for arbitrary custom domains is not yet implemented.
* Repository clone path for local Codex work: `/Users/yasyas/Library/Mobile Documents/com~apple~CloudDocs/проекты/blogcore`.
* Canonical GitHub repo: `yasyarik/blogcore`; local clone currently uses HTTPS remote because SSH publickey auth was unavailable locally.
* Important environment variables:
  - `PORT` default `3299`.
  - `ADMIN_HOSTS` default `blog.yas.ooo,127.0.0.1,localhost`.
  - `CNAME_TARGET` default `blog.yas.ooo`.
  - `HOSTED_BLOG_IPS` default `72.61.1.109`.
  - `GEMINI_API_KEY` or `GOOGLE_API_KEY` enables Gemini site analysis and article generation.
  - `GEMINI_TEXT_MODEL`, `GEMINI_MODEL_TEXT`, or `GEMINI_MODEL` can override the text model.
* Never store secrets or raw `.env` values in memory files.

## 7. Known pitfalls
* Source-authoritative imported/legacy job previews must not use the generic Blog Core renderer. If the source factory has no native unpublished preview, open the recorded source-site URL or show a clear unavailable state instead of faking a Blog Core-styled page.

* Imported/static site fixes must preserve the site's own tracked static source and stylesheet. For AIREP24-style static pages, do not republish through a generic factory/template pipeline for a surgical copy fix; restore from the site repo/webroot source first, then change only the requested markup.


* `data/blog_core.sqlite3` is ignored; Git commits do not preserve connected sites/jobs/theme profiles.
* The scanner handoff idempotency mapping is stored in the ignored `source_scanner_drafts` SQLite table; do not reconstruct it by title matching.
* `previews/` is ignored and regenerated.
* The live catchall nginx config is important for CNAME routing but is not currently represented in `deploy/nginx-blog.yas.ooo.conf`.
* HTTPS for arbitrary CNAME domains is not production-complete until certificate automation is added.
* Reddit may return `429 Too Many Requests`; topic discovery must surface it as a note/warning, not as a selectable signal card.
* Replaced/deprecated 2026-07-05: Google News RSS must not be used or labelled as a trend source. Discovery now uses Google autocomplete/search suggestions as a non-news popular-search signal source; this is still not the official Google Trends API.
* Do not turn Discovery into a local event or trade-promo feed. Results like a city wine festival, local guide, `Indies to receive £250 for Bordeaux Wine Month`, or retailer campaign should be filtered out even if they contain topical words.
* Do not make the Discovery period selector appear to apply to every source. It applies to Reddit discussions only; search-demand/autocomplete signals have no date filter.
* `install-blog` writes static files into `root_path/blog`; avoid using it for external sites with no local webroot.
* Theme scan depends on public HTML/CSS structure and may fail or capture weak design context for SPA-heavy or protected sites.
* If Gemini env vars are missing, `Scan design` still succeeds but topic-profile inference falls back to homepage title/description heuristics. This should be treated as degraded behavior, not the desired production path.
* `SEO_MEMORY.md` had an older note that dynamic sitemap expansion was not implemented. As of the imported/generated content job renderer, that note is replaced for hosted CNAME blogs; local static install still lacks final article publishing/export parity.
* Replaced/deprecated 2026-07-03: Existing blog import no longer has to rely on `sitemap_index.xml` for local VPS sites with `root_path`. For local sites such as `yas.wine`, direct webroot discovery is the authoritative inventory path.
* Production API may reject default Python `urllib` requests with `403`; use a normal User-Agent for scripted verification/import calls.
* Factory job messages may contain large JSON payloads from import/article-idea jobs. UI must render summarized job messages, not raw `publish_jobs.message`, or the dashboard becomes unreadable.
* Do not collapse content queue, discovery, distribution, setup, and activity logs into one long page again; keep these concerns separated in the tabbed manage UI.
* Do not show `Generate draft` on `IMPORTED` records; that makes already-published source pages look like unpublished tasks.
* Do not render per-channel social status as full-width text buttons/pills inside content cards; use compact icons with tooltips.
* Do not use a large text button for `Open live page` in content cards; use the compact external-link icon.
* Do not mix imported multilingual content in one default Content inventory list; default to a concrete language and require explicit language switching.
* Do not sort language-specific inventories by import timestamp/id; this makes each language show different first articles. Use normalized base path sorting instead.
* Do not place planned/future publication tasks in the Content inventory area; keep them at the bottom of Distribution below social channel settings.
* Do not render content pagination both above and below the cards, and do not use verbose `Page`/`Showing` text there.
* Do not show Publish Channels, include-link checkboxes, and connection status as three separate repeated channel sections. Use one unified card per social provider.
* Do not show active-looking `Connect` buttons for social providers without a credential setup/test path. Setup is the place to enter keys/tokens and test connections.
* Large imports need pagination in the Content inventory. Do not return to a hard-coded latest-24 list without navigation.
* Do not confuse Blog Core Content inventory pagination with public source-site blog pagination. `yas.wine/blog/` is a static public page in `/var/www/yaswine/blog/index.html`; its visible pagination must be fixed in that webroot.
* Do not render local imported-site draft previews with the generic Blog Core shell; that makes operators review the wrong design. Use the source site's local HTML template and assets.
* Do not leave Blog Core preview-only asset URLs or TOC `#anchor` links relative inside source-site templates that contain `<base>`, or browsers will resolve them against the source domain instead of the Blog Core preview page.
* Do not solve missing source-site blocks such as recommendations/newsletter locally per domain. Preserve recognizable post-article template sections generically for all imported local sites.
* Do not show setup/bootstrap actions on imported live-site cards; scanning/building/installing is for new Blog Core sites, not already imported production blogs.
* Do not generate imported legacy factory jobs with the generic Blog Core prompt. If the source factory rejects a draft, surface that error instead of keeping a weaker Blog Core-generated draft.
* Do not remove article TOC, FAQ, body figures, tables, ordered lists, quotes, length validation, or real article image generation when changing the structured article schema/prompt.
* Do not make operators delete a planned/content task just to fix a bad generated draft. Provide explicit regeneration for `DRAFT` tasks.
* Do not represent active `GENERATING` tasks as only a static badge. Show motion/progress, latest log/status text, and auto-refresh when finished.
* Do not rely only on in-memory daemon threads to finish legacy/source factory synchronization. PM2/Gunicorn restarts can kill those threads while the source factory continues and finishes; polling/status endpoints must be able to recover and sync the finished draft.
* For AIREP24 comparison pages, watch for old `/compare/...` static paths alongside canonical `/comparisons/...` paths. A fixed Blog Core draft can still appear broken publicly if an old static alias is serving stale shortened HTML.
* Factory v3 article pages must not render a second title/subtitle immediately after the hero. Keep the original article media/layout structure, including the top `article-head` image where applicable, but remove only the duplicated heading and lead copy from that block.
* Do not invent Gemini Image aspect ratios. Check provider-supported values before changing image generation contracts.

## 8. Decisions log

### 2026-07-21 — Explicit native publication scheduling

* Decision: Use a separate single PM2 worker and a per-job UTC `scheduled_for` value for automated page publication.
* Reason: The former cadence setting was UI/database-only. Explicit per-job scheduling avoids accidental publication of unrelated drafts and preserves source factories as the template and publisher authority.
* Files/areas affected: `app.py` scheduler contract, `scheduler.py`, `run-scheduler.sh`, `content_jobs` SQLite migration, PM2 deployment.
* Replaced/deprecated: A `publishing_cadence` value by itself is not treated as an active scheduler.

### 2026-07-21 — Source-factory blog validation alignment

* Decision: Align the source-factory writer brief with its blog validator: six to eight H2 sections, at most twelve H3 sections, and contextual blog links only where no real non-blog link inventory is supplied.
* Reason: The old source prompt demanded 20-40 H3 while the validator capped articles at 16, and it required a non-blog link that the blog-generation contract did not provide.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/generate.py`, `/var/www/content-factory-solocruz/factory/validate.py`.
* Replaced/deprecated: The contradictory 20-40 H3 blog instruction and impossible non-blog link requirement.

### 2026-07-21 — Native SEO-page article asset URLs

* Decision: Native SEO-page rendering resolves generated article media from the shared absolute `/blog/` asset folder.
* Reason: SEO pages are published in nested route directories, so bare media filenames incorrectly resolve relative to the page URL and make otherwise generated hero/inline images appear missing.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/seo_waitlist.py`.
* Replaced/deprecated: Relative generated article-media URLs in nested native SEO pages.

### 2026-07-21 — Native source-site chrome

* Decision: Native static publication extracts the header and footer from the source site's locale homepage and loads its existing CSS/JS assets.
* Reason: A source factory is a control-plane publisher, not a replacement theme. Its fallback chrome is visibly incomplete and must only be used when source chrome is unavailable.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/seo_waitlist.py`.
* Replaced/deprecated: Default factory navigation/footer on pages for sites that already provide native chrome.

### 2026-07-21 — Native page identity and language links

* Decision: Native static pages copy favicon/manifest identity tags from the source homepage. A copied language switch is rewritten to link only to published locales of the current canonical page; it is omitted when no translation exists.
* Reason: A homepage language menu on an article silently sends a reader away from the article, and generic factory pages must not show a browser icon that differs from the connected site.
* Files/areas affected: `/var/www/content-factory-solocruz/factory/seo_waitlist.py`.
* Replaced/deprecated: Reusing source-homepage language URLs verbatim on article pages and dropping source favicon assets from generated page heads.

### 2026-07-21 — SoloCruz article locale set

* Decision: A multilingual SoloCruz article is a canonical group of native source-factory jobs, one per published locale and native route. Publish the complete set, then re-publish each member so hreflang and the native language switch see every real counterpart.
* Reason: A single EN job cannot provide translations; copying a homepage switch is not an acceptable substitute for article-localized routes.
* Files/areas affected: source-factory job records and `/var/www/content-factory-solocruz/factory/seo_waitlist.py` publication behavior.
* Replaced/deprecated: Treating a single source job as a completed multilingual article.

### 2026-07-21 — Native SEO publication index and hero contract

* Decision: Native SEO blog publication must update the matching locale blog index and feed while preserving manually authored index cards; factory cards are maintained in a separate marked block. When a hero image exists, render it as unobstructed full-height media rather than placing generic copy over it.
* Reason: A published page is incomplete when it is absent from `/blog/`, and an image asset loses its purpose when template text obscures it.
* Files/areas affected: `/var/www/content-factory-solocruz/app.py`, `factory/landing.py`, and `factory/seo_waitlist.py`.
* Known issue: SoloCruz sitemap files are rebuilt and publicly referenced in `robots.txt`, but automated Google Search Console submission is not operational because the configured service-account credential file is absent. Do not claim a submission succeeded until an authorized credential is configured.

### 2026-07-21 — Source-factory publishing adapter audit

* Decision: Keep each source factory's native rendering adapter where it already preserves site chrome and asset behavior; do not force a single SoloCruz renderer onto unrelated sites.
* Reason: Published URL and media contracts differ by site. The SoloCruz nested-route asset fix is not evidence that YAS Wine, My UGC Studio, LaycanMatch, PipsAlerts, or AIREP24 use the same path model.
* Files/areas affected: source-factory audit across YAS Wine, My UGC Studio, SoloCruz, LaycanMatch, AIREP24, and PipsAlerts.
* Known issue: An old AIREP24 French job is marked published at a now-missing URL. It must be repaired through an explicit locale/path migration, not automated republishing.

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

### 2026-07-01 — Topic discovery must prioritize usable signals over filled grids

* Decision: Google/Reddit source errors are returned as warnings, not selectable cards. Reddit results must be top discussions and strongly title-relevant to the site topic, with a real site-topic anchor plus context. Low-relevance Google/Reddit results should be filtered instead of padding the grid.
* Reason: The dashboard should generate useful article ideas from strong signals, not from rate-limit errors or unrelated posts.
* Files/areas affected: `app.py` topic signal fetchers and manage-page signal UI.
* Replaced/deprecated: Displaying disabled error cards such as `Reddit unavailable: HTTP Error 429`.

### 2026-07-01 — Blog Core must reach YAS Wine factory parity per site

* Decision: Blog Core should preserve the operational capabilities of `/var/www/content-factory-yaswine`, but with every setting/job/social connection scoped by `site_id`.
* Reason: Blog Core is meant to become a universal multi-site article factory, not a single-site wine factory clone.
* Files/areas affected: `app.py`, `docs/FACTORY_PARITY.md`, future factory/social/publish modules.
* Replaced/deprecated: One-site global factory settings and wine-only prompt assumptions.


### 2026-07-01 — Import existing blogs without changing live URLs

* Decision: Existing `/blog/` articles should be scanned from sitemap/index URLs and imported into Blog Core as `content_jobs` with `status=IMPORTED`.
* Reason: This lets sites such as `yas.wine` or `airep24.com` move onto Blog Core without losing indexed URLs, metadata, or existing article HTML.
* Files/areas affected: `app.py` import scanner/import endpoints and hosted blog renderer.
* Replaced/deprecated: Rebuilding or overwriting existing blog content as the first migration step.

### 2026-07-03 — Keep project memory self-updating after local repo setup

* Decision: Treat repository memory files as the durable source of truth for future Codex runs and require a final memory-status line after every task.
* Reason: The project is now in a separate local clone and future sessions may start after context compaction or from a fresh Codex launch.
* Files/areas affected: `AGENTS.md`, `docs/PROJECT_MEMORY.md`, `docs/CHANGELOG_AI.md`, `docs/SEO_MEMORY.md`, `docs/DEPLOYMENT.md`.
* Replaced/deprecated: Relying on the current chat or older VPS-only context as the only memory source.

### 2026-07-03 — Imported blogs are managed in place, not mirrored by default

* Decision: For existing imported blogs, Blog Core should be the management/control plane and publish generated updates/articles back to the same original site locations and URL structure. Blog Core should not default to hosting an indexed second copy. For new blogs created entirely by Blog Core, Blog Core may fully host/publish the blog.
* Reason: Imported sites such as `yas.wine` already have working indexed blogs. The goal is to preserve those URLs and operations while adding a stronger dashboard/factory layer.
* Files/areas affected: Import model, publishing/export pipeline, hosted renderer SEO rules, future local/CMS/static publisher.
* Replaced/deprecated: Treating all imported content as if it should become public under Blog Core-hosted URLs.

### 2026-07-03 — Hide imported hub pages from content work lists

* Decision: Keep imported section index pages in metadata, but hide them from the Content inventory and paginate the visible records.
* Reason: Pages such as `https://yas.wine/blog/` are blog listing/hub pages, not article records or publication tasks. Showing them beside articles confused the imported-content workflow.
* Files/areas affected: `app.py` content job listing/rendering and `/api/sites/<id>/content-jobs`.
* Replaced/deprecated: Showing all latest imported `content_jobs` with `limit 24`, including `/blog/` and other section indexes, without pagination.

### 2026-07-05 — Discovery uses non-news topic demand

* Decision: Replace Google News RSS-based discovery with Google autocomplete/search suggestions plus Reddit top discussions. Apply this globally to all current and future sites.
* Reason: Blog Core Discovery should find broad popular topic demand, not local news, events, festivals, campaigns, or trade promotions.
* Files/areas affected: `app.py` topic signal API/UI, `docs/INTEGRATIONS.md`.
* Replaced/deprecated: Treating Google News RSS results as trend/topic signals.

### 2026-07-05 — Discovery ideas are reviewed before queueing

* Decision: Discovery now separates signal selection, article idea generation, operator idea selection, and queue creation. Similarity checks run before ideas are shown and again before selected ideas become planned jobs.
* Reason: Operators need to choose from generated article topics, and Blog Core must avoid suggesting/queueing near-duplicates of already published/imported or planned site content.
* Files/areas affected: `app.py` Discovery API/UI and `content_jobs` queue creation.
* Replaced/deprecated: Immediately creating `content_jobs` from checked Discovery signals.

### 2026-07-05 — Pinterest social drafts use native pin specs

* Decision: Add Pinterest as a per-site social channel and generate native pin draft specs instead of treating it as a plain text post.
* Reason: Pinterest needs vertical image creative, overlay/caption text, description, alt text, and destination URL metadata based on the article.
* Files/areas affected: `app.py` social provider config, social draft generation, Distribution/Setup UI, SQLite migrations.
* Replaced/deprecated: Treating all social channels as only text-length-limited post drafts.

### 2026-07-05 — Instagram drafts must show real publishable creatives

* Decision: Add Instagram as a per-site social channel whose drafts are carousel creatives with a caption and real 4:5 JPEG slide files generated by Gemini Image.
* Reason: Operators need to see the actual visual result that the factory will publish to Instagram, not a fast SVG/layout mockup.
* Files/areas affected: `app.py` social provider config, social draft generation, `social_posts`, ignored `data/social_assets`.
* Replaced/deprecated: Using SVG or placeholder-only previews for Instagram carousel review.

### 2026-07-05 — Instagram publishing uses an intermediary

* Decision: Treat Instagram as a per-site channel backed by a third-party publishing server. Blog Core stores intermediary API credentials and generated creatives; it must not directly publish through Instagram Graph API.
* Reason: The project publishes Instagram through a separate server-side intermediary.
* Files/areas affected: `app.py` Instagram social provider config, Setup credential labels, future publish route.
* Replaced/deprecated: Direct Instagram Graph API publishing assumptions in Blog Core.


### 2026-07-09 — Recover legacy factory drafts during status polling

* Decision: `GET /api/sites/<site_id>/content-jobs/<job_id>` re-checks legacy/source factory jobs that are still `GENERATING` in Blog Core and syncs completed `READY`/`PUBLISHED` drafts back into Blog Core.
* Reason: Legacy generation starts asynchronously; Blog Core PM2/Gunicorn restarts can kill the in-memory sync thread while the source factory continues and finishes successfully.
* Files/areas affected: `app.py` legacy factory generation/status sync and planned-publications polling.
* Replaced/deprecated: Assuming the original daemon thread is the only path that can move a legacy job from `GENERATING` to `DRAFT`.

### 2026-07-10 — Preview source-factory drafts natively

* Decision: For a source-authoritative `DRAFT` with a v3 payload, Blog Core proxies a native preview built by the original factory. The factory temporarily stages the payload and builds it without publishing, then binds the draft fields into semantic slots of the actual current source-page HTML template from the local webroot. The factory restores the v3 source files afterwards. Blog Core adds the source origin as `<base>` so CSS and asset URLs resolve to the real site.
* Reason: A generic Blog Core renderer, a stale v3 shell, or v3 markup injected into a live shell can all show the wrong page template. Preview must retain the live page's actual hero, article blocks, TOC, FAQ, recommendations, header/footer, and source-specific classes while replacing content values only.
* Files/areas affected: `Blog Core app.py` source-factory preview proxy; `content-factory-airep24/app.py` native v3 preview builder.
* Replaced/deprecated: Redirecting every source-authoritative draft preview to the live source URL, rendering it with the generic Blog Core/local-template preview shell, using a stale factory v3 shell, or injecting foreign v3 layout markup into the current source-site shell.

### 2026-07-13 — Preserve canonical paths when rewriting legacy content

* Decision: A queued content job can set `sources_json.preserveSlug=true` to lock its existing slug. Generic Blog Core generation may rewrite the title and body but must retain that canonical slug.
* Reason: Rewriting legacy content should improve the page without breaking its established URL, inbound links, or search history.
* Files/areas affected: `app.py` generic draft generation; `content_jobs.sources_json` migration metadata.
* Replaced/deprecated: Allowing a model-proposed slug to replace a preassigned canonical legacy path.

### 2026-07-13 — YAS legacy blog rewrite queue

* Decision: `yas.ooo` is connected in Blog Core as a local site rooted at `/opt/yas-ooo`. Its 12 existing English `/blog/<slug>/` topics are queued for full rewrites, not imported as duplicate public content. Its Next app reads Blog Core-managed JSON records from `data/blog-core/drafts` and `data/blog-core/published`.
* Reason: Blog Core should become the control plane and factory for future YAS content while preserving existing URLs. Draft generation and publishing remain separate actions; Preview writes only a noindex draft record, while Publish atomically writes the public record.
* Files/areas affected: ignored live `data/blog_core.sqlite3` site/job records; Blog Core `native-content-store` adapter; `/opt/yas-ooo` dynamic blog/home/sitemap content readers and preview route.
* Replaced/deprecated: Treating legacy YAS articles as a separate migration/copy target.

### 2026-07-13 — Native Next content-store publisher contract

* Decision: For a local Next site marked with `publicationMode=native_next_content_store` (the former YAS compatibility value `native_yas_publisher` remains supported), Blog Core saves generated drafts as JSON under `<root>/data/blog-core/drafts/<job>.json`. Preview redirects to `/content-preview/<job>` on the source site; explicit Publish atomically writes `<root>/data/blog-core/published/<slug>.json` and marks the Blog Core job `PUBLISHED`.
* Reason: The source site retains its own components and visual system. Content changes do not require reauthoring TypeScript arrays, rebuilding the website, or using the generic Blog Core static installer.
* Files/areas affected: `app.py` publication and preview routes; YAS `src/lib/managed-content.ts`, `ManagedArticle`, dynamic `/blog`, `/blog/[slug]`, `/content-preview/[jobId]`, homepage insights, and sitemap.
* Replaced/deprecated: Generic local HTML preview/install for YAS-generated content.

### 2026-07-13 — Native SEO use-case content type for YAS

* Decision: YAS has an indexable `/use-cases/` hub and four initial decision-oriented money pages. The Next content store recognizes `use_case`, `seo_money_page`, and `seo-money-page` publication types as managed `use_case` content, separate from the blog feed.
* Reason: Commercial intent pages need their own information architecture, service linkage, canonical routes, and sitemap entries; they should not be mixed into editorial blog output.
* Files/areas affected: YAS `src/content/use-cases.ts`, `/use-cases` routes, header navigation, dynamic sitemap, and the Blog Core native content-store payload.
* Replaced/deprecated: Treating every generated content task as a blog article regardless of its target page type.

### 2026-07-13 — Discovery routes SEO money pages by content type

* Decision: The universal Discovery journalist prompt may return `contentType=seo_money_page` only for a durable, service-aligned use case. Queueing normalizes this to a canonical `/use-cases/<slug>/` target with `pageType=seo_money_page`; editorial ideas retain `/blog/<slug>/`.
* Reason: Content type must drive destination and publication behavior. A commercial intent signal alone is not enough to make a money page.
* Files/areas affected: `app.py` Discovery prompt, idea sanitizer, and article-idea queue route.
* Replaced/deprecated: Defaulting all Discovery output to blog paths after the model had classified a page as a money page.

### 2026-07-13 — Native YAS sitemap is publication-driven

* Decision: The YAS `sitemap.xml` route is dynamic and reads the native content store at request time.
* Reason: A Blog Core Publish action must expose its new canonical blog/use-case URL to crawlers immediately without a Next rebuild.
* Files/areas affected: `/opt/yas-ooo/src/app/sitemap.ts`.
* Replaced/deprecated: Build-time-only sitemap output for native published content.

### 2026-07-13 — Preserve the YAS use-cases visual system for factory output

* Decision: The user-owned YAS `/use-cases/` cinematic design is the authoritative template. Published factory use cases append to its existing operating-case list, and their detail/preview pages use the same dark `useCasesFilm` visual system.
* Reason: Blog Core is the content factory/control plane, not a replacement for the source site's design. A use-case publication must not fall back to the generic light article template.
* Files/areas affected: YAS `use-cases/page.tsx`, `use-cases/[slug]/page.tsx`, `use-cases.module.css`, `ManagedUseCasePage`, and `content-preview/[jobId]/page.tsx`.
* Replaced/deprecated: Rendering managed use-case detail and preview pages through `ManagedArticlePage`.

### 2026-07-13 — YAS content queue focus excludes Shopify

* Decision: Remove the queued YAS rewrite tasks whose subject is Shopify. The current YAS editorial focus is not Shopify.
* Reason: The queue must reflect the active positioning of the site rather than preserve historical topic inventory by default.
* Files/areas affected: Ignored live `data/blog_core.sqlite3` YAS planned content jobs.
* Replaced/deprecated: The initial Shopify-oriented subset of the YAS legacy rewrite queue.

### 2026-07-13 — Receive finished YAS Studio drafts as Blog Core tasks

* Decision: Accept explicitly selected YAS Source Scanner drafts through an authenticated endpoint and store them as native `yas.ooo` `DRAFT` jobs.
* Reason: Studio is the authoring desk; Blog Core already owns the native YAS review, publication and distribution controls.
* Files/areas affected: `source_scanner_drafts`, `content_jobs`, native YAS draft store, source-scanner integration API.
* Replaced/deprecated: The old scanner-brief-only handoff does not represent an authored Studio article and is not used for this workflow.

### 2026-07-13 — Per-site Zernio transport for social publishing

* Decision: X/Twitter, Pinterest, Instagram, Threads, and Reddit use one per-site Zernio connection with explicit connected-account mappings. Blog Core owns per-channel draft generation, native assets, validation, review, and explicit submission; Zernio owns OAuth accounts and delivery.
* Reason: The same five networks must not be configured or published through unrelated direct integrations. Per-site account mappings prevent content from being sent to the wrong brand account.
* Files/areas affected: `app.py` social connections, drafts, Zernio publish route, Setup/Distribution UI, ignored social assets and social post records.
* Replaced/deprecated: Direct per-network connection forms for X, Pinterest, Instagram, and Threads. Existing legacy credentials remain stored but are not considered active for these channels.

### 2026-07-13 — Native social editorial contracts

* Decision: Social drafts must select a channel-native editorial format rather than produce a generic article summary. Instagram carousels carry a validated type/slide structure; Threads carries a conversation format; X can carry a validated thread sequence; Pinterest produces a finished 2:3 JPEG Pin; Telegram and Tumblr drafts include their own editorial image metadata; Reddit carries a community-first title/body and site-configured subreddit rules.
* Reason: Character limits alone do not produce content that fits a network or earns meaningful engagement.
* Files/areas affected: `app.py` social prompt builders, validators, asset generation, social review routes.
* Replaced/deprecated: One generic text-only social prompt for all providers.

### 2026-07-13 — LinkedIn personal-profile OAuth connection

* Decision: Blog Core provides a server-side OAuth authorization-code flow for LinkedIn personal-profile publishing. The configured callback is `https://blog.yas.ooo/oauth/linkedin/callback`; successful authorization stores only the issued access token and `urn:li:person:<id>` for the selected site.
* Reason: Client ID/secret are application credentials, not a publish token or author identity. Operators should not copy temporary access tokens or URNs manually.
* Files/areas affected: server-only `.env` (ignored), `app.py` OAuth start/callback routes and LinkedIn Setup card.
* Replaced/deprecated: Pasting a manually obtained LinkedIn access token and personal URN into the Setup form.

### 2026-07-13 — Podcast production is a separate reviewable content workflow

* Decision: Blog Core creates podcast episodes from existing article content through a per-site workflow: script generation, Gemini TTS audio generation, review, then explicit publication to a stable Blog Core episode URL and RSS feed.
* Reason: Audio generation must not implicitly publish an episode or overwrite an imported site's native design. Podcast assets and publication state need the same traceability as article and social work.
* Files/areas affected: `podcast_settings`, `podcast_episodes`, ignored `data/podcast_assets/`, Podcast dashboard tab, podcast API/routes and RSS feed.
* Replaced/deprecated: Treating an article narration as an untracked one-off asset or automatic source-site publication.

### 2026-07-15 — Source-factory bindings make Blog Core an imported-site control plane

* Decision: Imported sites with their own compatible factory are bound through `site_factory_bindings`. Blog Core creates new work in that source factory, then delegates generation, native preview, and explicit publication to it while synchronizing the job state into its own dashboard.
* Reason: The source factory remains authoritative for its current template, image workflow, validation, URLs, and deploy process. Blog Core must manage that workflow without creating a parallel public blog or modifying the source design.
* Files/areas affected: `app.py` factory-binding helpers and new-job delegation; ignored `data/blog_core.sqlite3` bindings and imported job inventory.
* Replaced/deprecated: Creating a generic Blog Core job for a source-authoritative site and attempting to render or publish it through the generic pipeline.

### 2026-07-15 — PipsAlerts factory imported as source-authoritative

* Decision: `pipsalerts.com` is managed through its existing `content-factory-pipsalerts` FastAPI factory on the same VPS. Its public content stays at `/guides/{slug}/`; the local Next site and factory remain the only publisher/template authority.
* Reason: PipsAlerts already has a working factory and native guide architecture. The dashboard should expose its content inventory and initiate work in the existing system rather than recreate the guides in Blog Core.
* Files/areas affected: PipsAlerts site record, `site_factory_bindings`, and imported `content_jobs` in ignored Blog Core SQLite data.
* Replaced/deprecated: Treating the PipsAlerts guide collection as a new generic `/blog/` installation.

### 2026-07-16 — SoloCruz source factory bound to Blog Core

* Decision: `solocruz.com` is managed through `content-factory-solocruz` as a source-authoritative factory. Blog Core passes the complete native page contract when it creates a source job: content type, page kind, locale, target path, and canonical group.
* Reason: A source factory needs more than a topic and slug to preserve a site's path structure and multilingual publication model. This lets Blog Core manage a single canonical task while the source factory creates its own localized public pages.
* Files/areas affected: `app.py` delegation payload; ignored Blog Core binding data; `/var/www/content-factory-solocruz` server-only factory configuration and preview implementation.
* Replaced/deprecated: The unbound SoloCruz inventory-only integration and the factory's placeholder webroot/domain configuration.

### 2026-07-18 — YAS Wine factory bound as the source-authoritative publisher

* Decision: `yas.wine` is bound to `content-factory-yaswine` at `127.0.0.1:3199`. Blog Core manages its native job queue and delegates Generate, Preview, Regenerate, and explicit Publish to that factory; the factory remains authoritative for the live wine blog and SEO section pages.
* Reason: The original local factory owns multilingual output, images, validation, source template, static page writes, indexes, and sitemaps. Blog Core must be the dashboard without replacing these site-specific publication contracts.
* Files/areas affected: `site_factory_bindings`, linked YAS Wine `content_jobs` in ignored SQLite data, Blog Core legacy regeneration behavior, and the private template configuration in `/var/www/content-factory-yaswine`.
* Replaced/deprecated: Inventory-only YAS Wine import without source job linkage.

### 2026-07-18 — Complete connected-site source-factory control plane

* Decision: Every connected site with a compatible local content factory is bound through `site_factory_bindings`, and its historical source jobs are linked into Blog Core by a rerunnable inventory synchronization. `yas.ooo` remains a native content-store integration rather than a source-factory binding.
* Reason: The dashboard must operate the original factory for all imported sites without re-rendering, relocating, or publishing generic Blog Core pages into those sites.
* Files/areas affected: `app.py` source endpoint resolver plus inventory-sync/backfill APIs; ignored Blog Core SQLite bindings and source-job mappings; `docs/INTEGRATIONS.md`.
* Replaced/deprecated: Factory-name endpoint defaults as the primary routing mechanism. They remain only for legacy records that predate a binding.

### 2026-07-23 — Native content-store sites use Blog Core as their factory

* Decision: A site with `sites.access_type=native_content_store` uses Blog Core's universal generation, review, scheduling, and explicit publication lifecycle. Blog Core writes atomic JSON records into `{root_path}/data/blog-core/drafts` and `{root_path}/data/blog-core/published`; the site-owned renderer consumes those records.
* Reason: Newly integrated first-party sites do not need a duplicate legacy factory service. They still require native preview and publication under their own domain and visual system.
* Files/areas affected: `app.py` native-store detection; site-owned renderer deployments such as `deploy/georivo/`.
* Replaced/deprecated: Treating the native content-store contract as a `yas.ooo`-only special case.

### 2026-07-23 — Georivo native journal integration

* Decision: Georivo site 14 is a first-party Blog Core factory site with local native content storage at `/var/www/georivo-blog`. Nginx keeps the existing product upstream intact and routes only `/blog`, `/content-preview`, and `/sitemap.xml` to the local renderer.
* Reason: The live product application is currently proxied from an external `chatgpt.site` origin and has no `/blog`. A local route adapter gives Blog Core full editorial control without rebuilding or modifying the product application.
* Files/areas affected: `deploy/georivo/`, live `/var/www/georivo-blog`, `/etc/nginx/conf.d/georivo.com.conf`, ignored Blog Core SQLite site/profile data.
* Replaced/deprecated: External design scanning followed by a generic Blog Core-hosted mirror for Georivo.

### 2026-07-23 — Georivo renderer must reuse exact source visual chrome

* Decision: The Georivo journal uses the source site's `header.nav.glass`, `brand-logo`, `nav-links`, `footer-top`, `footer-links`, and `footer-bottom` DOM/CSS contracts. Its content follows the same photographic hero, cream editorial band, dark content band, photographic CTA, Arial display copy, Georgia emphasis, Geist metadata, lime action, and 14-28 px radius system.
* Reason: A separate theme that merely reused Georivo colors and fonts did not look like the product site. Exact source chrome and responsive behavior are required for a native integration.
* Files/areas affected: `deploy/georivo/app.py`, `deploy/georivo/georivo-blog.css`, `deploy/georivo/georivo-blog-nav.js`.
* Replaced/deprecated: The initial custom dark `site-header`/`site-footer` renderer and oversized standalone logo treatment.

### 2026-07-24 — Resolve Georivo's native hashed stylesheet dynamically

* Decision: The Georivo blog renderer discovers the current `/assets/index-*.css` reference from the live product homepage, validates the path against a strict asset pattern, and caches it briefly. A configurable current fallback remains available when the upstream homepage cannot be read.
* Reason: The externally hosted product rebuilds its CSS under new hashed filenames. Pinning one hash caused the blog's otherwise native header/footer structure to render unstyled as soon as the upstream asset changed.
* Files/areas affected: `deploy/georivo/app.py` and the live `/var/www/georivo-blog/app.py`.
* Replaced/deprecated: Hard-coded `/assets/index-22jNjtDO.css`.

### 2026-07-24 — Native content-store multilingual contract

* Decision: One native content-store task generates the base article plus full structured localizations for every language in `sites.languages`. Localizations are stored in `content_job_localizations` by `job_id + language` and exported inside the native JSON record's `translations` map; they are not separate dashboard jobs.
* Reason: Editors manage one topic and publication decision while the site receives complete language variants with the same slug, structure, facts, FAQ, and generated image files.
* Files/areas affected: `app.py`, native content-store JSON, and site-owned renderers such as `deploy/georivo/`.
* Replaced/deprecated: Native content-store generation that wrote only the site's first configured language.

### 2026-07-24 — Georivo multilingual URL and SEO model

* Decision: Georivo uses EN as its base language at `/blog/` and DE/ES/FR/RU at `/{language}/blog/`. Article slugs remain identical across languages. The native renderer localizes its interface, links language variants, emits per-language canonical plus hreflang/x-default, and includes localized variants in the sitemap.
* Reason: Language switching must keep the reader on the same article and search engines must receive an explicit relationship between real translated pages.
* Files/areas affected: site 14 language settings, `deploy/georivo/`, live `/var/www/georivo-blog`, and `/etc/nginx/conf.d/georivo.com.conf`.
* Replaced/deprecated: Georivo as an English-only native journal.

### 2026-07-24 — Georivo first live multilingual article

* Decision: Georivo's first Blog Core-owned publication is the canonical task “How Remote Property Buyers Evaluate Location Before Booking a Viewing”, published at `/blog/remote-property-buyers-evaluate-location-before-viewing/` with DE/ES/FR/RU counterparts under their locale prefixes.
* Reason: It establishes the intended editorial territory through a real end-to-end native publication and proves one-task multilingual generation, media delivery, language routing, hreflang, index listing, and sitemap expansion.
* Files/areas affected: Blog Core site 14 database records and `/var/www/georivo-blog/data/blog-core/published/`.
* Replaced/deprecated: Georivo's connected-but-empty journal state.

### 2026-07-24 — Live source chrome is a global renderer contract

* Decision: Blog Core-owned hosted/CNAME pages and native renderers obtain current source `<header>`, `<footer>`, and stylesheet URLs from the connected site's `homepage_url` through shared `native_site_chrome.py`, cache briefly, and fall back to the saved design scan only when the source cannot be read.
* Reason: Copying source chrome into a renderer drifts as soon as account controls, language selectors, footer credits, navigation, or compiled assets change. Runtime source reuse keeps Blog Core content native without modifying the product application.
* Files/areas affected: `native_site_chrome.py`, `app.py` hosted rendering, and native adapters under `deploy/`.
* Replaced/deprecated: Hand-maintained header/footer copies in Blog Core-owned renderers and relying on a historical design scan as the public chrome authority.

### 2026-07-24 — Source-authoritative publisher boundary

* Decision: Imported sites bound to their own source factory do not use Blog Core's hosted chrome wrapper. Their source publisher must render the site's real template, header, footer, language routing, and assets.
* Reason: A universal wrapper cannot safely replace a source application's routing, hydration, authentication controls, or page-template contract.
* Files/areas affected: source-factory bindings and preview/publish adapters.
* Replaced/deprecated: Assuming one generic header/footer mechanism should overwrite source-authoritative factory output.

### 2026-07-24 — Georivo trend-led editorial territory

* Decision: Georivo's initial journal should build authority around the intersection of virtual property tours, real-estate photography, drone alternatives, interactive maps, digital twins, neighborhood context, remote-buyer decisions, and verifiable geospatial visualization. Raw Trends/search phrases are research signals, not article titles.
* Reason: Exact Georivo-specific phrases are often too low-volume for reliable Google Trends reporting. Broader parent topics reveal audience demand, while the final editorial angle must answer a real property-marketing decision and express Georivo's distinct location-story expertise.
* Files/areas affected: Georivo Discovery profile and future `/blog/` queue.
* Replaced/deprecated: Treating generic real-estate marketing news or copied trend-query wording as suitable Georivo article ideas.

## 9. Do not repeat

* Do not rely on local `/blog` installation for third-party sites; use CNAME hosting unless the local webroot is truly available.
* Do not delete installed target-site `/blog` files when removing a connected site from Blog Core.
* Do not commit SQLite database, generated previews, virtualenv, logs, or secrets.
* Do not treat Reddit availability as guaranteed; build and test degraded states.
* Do not assume chat context has all prior decisions; read memory first.
* Do not silently delete outdated memory. Mark replaced/deprecated and add the current version.
* Do not design imported-blog workflows as public mirrors by default. Preserve the source site's URLs and publish back in place unless the user explicitly asks for a cutover.
* Do not present raw Discovery signals as finished article topics. They are inputs for the journalist/SEO article idea generator.
* Do not let existing bad/generated content grant permission for future generic review/tutorial/listicle topics. Site editorial policy is inferred from stable site profile/settings, while existing content is used for context and duplicate checks.
* Do not fake a source-authoritative draft preview with Blog Core HTML, and do not run any `publish-*` v3 command merely to preview it. Build the source factory preview only, keep it `noindex`, and preserve the live webroot unchanged until the operator explicitly publishes.
* A source-factory preview must preserve the actual current source-page shell from that site's webroot, including head/CSS, header, footer, breadcrumbs, and current navigation/CTA links. Do not assume the factory's v3 shell is visually current.
* Preserve the source page's internal template classes and blocks too. Bind draft values to the existing hero/article/TOC/FAQ/recommendation slots rather than replacing a live page's content area with a different factory layout. If a new draft image has not been deployed to the source site, retain the existing template image instead of showing an empty media block.
* Draft previews must not show breadcrumb navigation unless it is explicitly part of the required public page view. When the source template has reusable inline-media components, bind real generated draft image files to those components using source-site absolute URLs; do not show empty image frames or generic image markup.
* Do not replace a user-authored source-site page design during integration. Extend its native data list/components and reuse its visual system for published and previewed factory content.
* Do not cross-post an article summary unchanged. Select the social format from the article's evidence, audience intent, and the target channel's native behaviour, then validate its channel-specific constraints before storing or sending it.
* Do not imply Gemini TTS prebuilt voices are voice cloning. A selected Gemini voice and per-site direction are supported; true custom/clone voice requires a separate Google Cloud Custom Voice arrangement and adapter.
* Do not auto-publish podcast audio after generation. A ready episode must be reviewed and explicitly published. Native embedding on an imported source site must use that source factory's adapter rather than Blog Core changing its public template.
* Do not bypass a configured source-factory binding for a new imported-site task. Create, generate, preview, and publish through the native source factory so the public URL, design, assets, and validations remain authoritative.
* Do not create a legacy source-factory binding for a first-party `native_content_store` site. Blog Core is already its factory; keep the native renderer focused on preview and publication.
* Do not claim a site integration is native because it shares colors or fonts. Match and verify the source DOM, computed header/footer dimensions, section rhythm, typography roles, controls, and responsive behavior.
* Do not delegate only a title and slug to a source factory. Preserve the planned task's native path, canonical group, type, and language in the source job payload.
* An explicit Regenerate action for a source-authoritative task must call the source factory even when the previous result is `READY` or `PUBLISHED`; merely re-syncing an old result is not regeneration.
